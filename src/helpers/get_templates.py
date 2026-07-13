from tomtom_interactions.models import (
    RouteResponse,
    TemplateBody,
    TimeGroupAdvanced,
    TimeSetAdvanced,
)
from constants import (
    TEMPLATE_END_DATE,
    TEMPLATE_START_DATE,
    DAYS_PER_PROJECT,
    DATE_RANGE_MODEL_ARROW_TIME_FORMAT,
)
from arrow import Arrow
from helpers.models import DateRange


ALL_DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def convert_time_sets(detail_time_sets: list) -> list[TimeSetAdvanced]:
    """
    Converts the detail response's time sets (dayToTimeRanges form) into the
    advanced time_groups form expected by POST /ts/.

    The source's day-of-week restrictions are deliberately dropped: each time
    set is extended to all seven days. Template sources are often single-day
    studies whose time sets only cover that day's weekday, and the platform
    rejects copies whose date ranges fall on uncovered weekdays.
    """
    converted: list[TimeSetAdvanced] = list()

    for time_set in detail_time_sets:
        time_ranges: list[str] = list()
        for day_ranges in time_set["dayToTimeRanges"]:
            for time_range in day_ranges["timeRanges"]:
                if time_range not in time_ranges:
                    time_ranges.append(time_range)

        converted.append(
            TimeSetAdvanced(
                name=time_set["name"],
                time_groups=[
                    TimeGroupAdvanced(days=day, times=time_ranges) for day in ALL_DAYS
                ],
            )
        )

    return converted


def generate_dateranges(start_date: Arrow, days_per_project: int, end_date: Arrow) -> list[DateRange]:
    date_range_list: list[DateRange] = list()
    start = start_date.clone()

    for shift in range(days_per_project):
        shifted_date = start.shift(days=shift)

        if shifted_date > end_date:
            print(date_range_list[0].to)
            print(date_range_list[-1].to)
            return date_range_list

        shifted_str = shifted_date.format(DATE_RANGE_MODEL_ARROW_TIME_FORMAT)

        date_range = {
            "name": shifted_str,
            "to": shifted_str,
            "days": [shifted_date.weekday()],
            "eligible_days": [shifted_date.weekday()],
            "from": shifted_str,
        }

        date_range_list.append(DateRange.model_validate(date_range))

    print(date_range_list[0].to)
    print(date_range_list[-1].to)
    return date_range_list


def generate_templates_body(
    date_ranges: list[DateRange], template_name: str, route_res: RouteResponse
) -> TemplateBody:
    return TemplateBody(
        name=template_name,
        network=[
            item.model_copy(update={"timezone": route_res.timezone})
            for item in route_res.network
        ],
        date_range=date_ranges,
        probe_source=route_res.probe_source,
        time_sets=[
            time_set.model_dump() for time_set in convert_time_sets(route_res.time_sets)
        ],
        is_time_sets_advanced=True,
        frcs=route_res.frcs,
        timezone=route_res.timezone,
        map_version=route_res.map_version,
    )


def generate_templates_bodies(
    route_response: RouteResponse, template_name: str
) -> list[TemplateBody]:
    template_bodies: list[TemplateBody] = list()

    start_date = TEMPLATE_START_DATE.clone()
    end_date = TEMPLATE_END_DATE

    while start_date < end_date:
        template_name_end_date = min(end_date, start_date.shift(days=DAYS_PER_PROJECT))
        daterange_template_name = f"{template_name} Updated ({start_date.format(DATE_RANGE_MODEL_ARROW_TIME_FORMAT)}-{template_name_end_date.format(DATE_RANGE_MODEL_ARROW_TIME_FORMAT)})"
        print(daterange_template_name)
        date_ranges = generate_dateranges(start_date, DAYS_PER_PROJECT, end_date)
        template = generate_templates_body(
            date_ranges, daterange_template_name, route_response
        )

        template_bodies.append(template)

        start_date = start_date.shift(days=DAYS_PER_PROJECT)

    return template_bodies
