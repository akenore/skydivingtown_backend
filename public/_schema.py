import graphene
from graphene_django import DjangoObjectType
from django.db.models import Count
from event.models import Event, Subscriber, EventDate, EventTime, EventOption
from django_countries import countries
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings


class EventType(DjangoObjectType):
    class Meta:
        model = Event
        fields = "__all__"


class EventOptionType(DjangoObjectType):
    class Meta:
        model = EventOption
        fields = "__all__"


class EventDateType(DjangoObjectType):
    class Meta:
        model = EventDate
        fields = "__all__"


class EventTimeType(DjangoObjectType):
    current_subscriber_count = graphene.Int()
    available_slots = graphene.Int()
    is_full = graphene.Boolean()

    class Meta:
        model = EventTime
        fields = "__all__"

    def resolve_current_subscriber_count(root, info):
        return root.current_subscriber_count

    def resolve_available_slots(root, info):
        return root.get_available_slots()

    def resolve_is_full(root, info):
        return root.is_full()


class SubscriberType(DjangoObjectType):
    class Meta:
        model = Subscriber
        fields = "__all__"


class CountryType(graphene.ObjectType):
    code = graphene.String()
    name = graphene.String()


class Query(graphene.ObjectType):
    all_events = graphene.List(EventType)
    all_event_dates = graphene.List(EventDateType, event_id=graphene.ID(required=True))
    all_event_times = graphene.List(EventTimeType, event_date_id=graphene.ID(required=True))
    all_subscribers = graphene.List(SubscriberType)
    all_countries = graphene.List(CountryType)

    def resolve_all_events(root, info):
        return Event.objects.all()

    def resolve_all_event_dates(root, info, event_id):
        return EventDate.objects.filter(event_id=event_id)

    def resolve_all_event_times(root, info, event_date_id):
        return EventTime.objects.filter(event_date_id=event_date_id)

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

        # Check if the event time is already full
        if event_time.is_full():
            raise Exception("This event time is already full.")

        subscriber = Subscriber(
            eventDate=event_time.event_date,
            eventTime=event_time,
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
        subscriber.save()

        # Add selected options if provided
        if options:
            event_options = EventOption.objects.filter(name__in=options)
            subscriber.options.set(event_options)

        # Send data to Brevo
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
        contact = sib_api_v3_sdk.CreateContact(
            email=email,
            attributes={"FNAME": name, "LNAME": surname, "SMS": phone},
            list_ids=[settings.BREVO_LIST_ID]
        )
        try:
            api_instance.create_contact(contact)
        except ApiException as e:
            print(f"Error adding contact to Brevo: {e}")

        return CreateSubscriber(subscriber=subscriber)


class Mutation(graphene.ObjectType):
    create_subscriber = CreateSubscriber.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
