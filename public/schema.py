import graphene
from graphene_django import DjangoObjectType
from django.db.models import Count, F
from event.models import Event, Subscriber, EventDate, EventOption
from django_countries import countries


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

    def resolve_current_subscriber_count(root, info):
        return root.current_subscriber_count


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
        event_date_id = graphene.ID(required=True)
        name = graphene.String(required=True)
        surname = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=True)
        birth_date = graphene.Date(required=True)
        gender = graphene.String(required=True)  # Radio button
        altitude = graphene.String(required=True)  # Radio button
        skydiver_option = graphene.String(required=True)  # Radio button
        country = graphene.String(required=True)
        region = graphene.String(required=True)
        options = graphene.List(graphene.String)  # Checkbox

    subscriber = graphene.Field(SubscriberType)

    def mutate(self, info, event_date_id, name, surname, email, phone, birth_date, gender, altitude, skydiver_option, country, region, options):
        event_date = EventDate.objects.get(pk=event_date_id)
        subscriber = Subscriber(
            eventDate=event_date,
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
        if options:
            event_options = EventOption.objects.filter(name__in=options)
            subscriber.options.set(event_options)
        return CreateSubscriber(subscriber=subscriber)


class Mutation(graphene.ObjectType):
    create_subscriber = CreateSubscriber.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
