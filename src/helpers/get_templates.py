from tomtom_interactions.models import RouteResponse, TemplateBody, DateRange
from constants import (
    TEMPLATE_END_DATE,
    TEMPLATE_START_DATE,
    DAYS_PER_PROJECT,
    DATE_RANGE_MODEL_ARROW_TIME_FORMAT,
)
from arrow import Arrow
from helpers.formatting import convert_v2_to_v1


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
        network=convert_v2_to_v1(route_res.network, route_res.timezone),
        date_range=date_ranges,
        probe_source=route_res.probe_source,
        time_sets=route_res.time_sets,
        frcs=route_res.frcs,
        timezone=route_res.timezone,
        map_version=route_res.map_version,
        map_type=route_res.map_type,
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
