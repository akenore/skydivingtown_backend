import graphene
from graphene_django import DjangoObjectType
from django.db.models import Count, F
from event.models import Event, Subscriber, EventDate, EventTime, EventOption
from django_countries import countries
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings


class EventType(DjangoObjectType):
    class Meta:
        model = Event
        fields = "__all__"


class SubscriberType(DjangoObjectType):
    class Meta:
        model = Subscriber
        fields = "__all__"


class EventDateType(DjangoObjectType):
    class Meta:
        model = EventDate
        fields = "__all__"

    event_times = graphene.List(lambda: EventTimeType)

    def resolve_event_times(self, info):
        return self.event_times.all().order_by('time')


class EventTimeType(DjangoObjectType):
    class Meta:
        model = EventTime
        fields = "__all__"

    current_subscriber_count = graphene.Int()
    available_slots = graphene.Int()
    is_full = graphene.Boolean()

    def resolve_current_subscriber_count(self, info):
        return self.current_subscriber_count

    def resolve_available_slots(self, info):
        return self.get_available_slots()

    def resolve_is_full(self, info):
        return self.is_full()


class EventOptionType(DjangoObjectType):
    class Meta:
        model = EventOption
        fields = "__all__"


class CountryType(graphene.ObjectType):
    code = graphene.String()
    name = graphene.String()


class Query(graphene.ObjectType):
    all_events = graphene.List(EventType)
    all_event_dates = graphene.List(
        EventDateType, event_id=graphene.ID(required=True))
    all_subscribers = graphene.List(SubscriberType)
    all_countries = graphene.List(CountryType)

    def resolve_all_events(root, info):
        return Event.objects.all()

    def resolve_all_event_dates(root, info, event_id):
        return EventDate.objects.filter(event_id=event_id)

    def resolve_all_subscribers(root, info):
        return Subscriber.objects.all()

    def resolve_all_countries(root, info):
        return [{'code': code, 'name': name} for code, name in countries]


class CreateSubscriber(graphene.Mutation):
    class Arguments:
        event_time_id = graphene.ID(required=True)
        name = graphene.String(required=True)
        surname = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=True)
        birth_date = graphene.Date(required=True)
        gender = graphene.String(required=True)
        altitude = graphene.String(required=True)
        skydiver_option = graphene.String(required=True)
        country = graphene.String(required=True)
        region = graphene.String(required=True)
        options = graphene.List(graphene.String)

    subscriber = graphene.Field(SubscriberType)

    def mutate(self, info, event_time_id, name, surname, email, phone, birth_date, gender, altitude, skydiver_option, country, region, options):
        event_time = EventTime.objects.get(pk=event_time_id)
        if event_time.is_full():
            raise graphene.GraphQLError("This event time is full.")

        subscriber = Subscriber(
            eventTime=event_time,
            eventDate=event_time.event_date,
            name=name,
            surname=surname,
            email=email,
            phone=phone,
            birthDate=birth_date,
            gender=gender,
            altitude=altitude,
            skydiverOption=skydiver_option,
            country=country,
            region=region
        )
        subscriber.full_clean()
        subscriber.save()

        if options:
            event_options = EventOption.objects.filter(name__in=options)
            subscriber.options.set(event_options)

        # Brevo API integration
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        api_instance = sib_api_v3_sdk.ContactsApi(
            sib_api_v3_sdk.ApiClient(configuration))
        contact = sib_api_v3_sdk.CreateContact(
            email=email,
            update_enabled = True,
            attributes={"FNAME": name, "LNAME": surname, "SMS": phone},
            list_ids=[2]
        )
        try:
            api_instance.create_contact(contact)
        except ApiException as e:
            print(f"Error adding contact to Brevo: {e}")

        return CreateSubscriber(subscriber=subscriber)


class Mutation(graphene.ObjectType):
    create_subscriber = CreateSubscriber.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
