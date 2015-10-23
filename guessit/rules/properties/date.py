#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Date and year
"""
from rebulk import Rebulk, RemoveMatchRule

from ..common.date import search_date, valid_year
from ..common.validators import seps_surround

DATE = Rebulk()

DATE = Rebulk()
DATE.defaults(validator=seps_surround)

DATE.regex(r"\d{4}", name="year", formatter=int,
           validator=lambda match: seps_surround(match) and valid_year(match.value))


def date(string, context):
    """
    Search for date in the string and retrieves match

    :param string:
    :return:
    """

    ret = search_date(string, context.get('date_year_first'), context.get('date_day_first'))
    if ret:
        return ret[0], ret[1], {'value': ret[2]}


DATE.functional(date, name="date")


class KeepMarkedYearInFilepart(RemoveMatchRule):
    """
    Keep first years marked with [](){} in filepart, or if no year is marked, ensure it won't override titles.
    """
    priority = 512  # Must be before title and filmTitle rules

    def when(self, matches, context):
        ret = []
        if len(matches.named('year')) > 1:
            for filepart in matches.markers.named('path'):
                years = matches.range(filepart.start, filepart.end, lambda match: match.name == 'year')
                if len(years) > 1:
                    group_years = []
                    ungroup_years = []
                    for year in years:
                        if matches.markers.at_match(year, lambda marker: marker.name == 'group'):
                            group_years.append(year)
                        else:
                            ungroup_years.append(year)
                    if group_years and ungroup_years:
                        ret.extend(ungroup_years)
                        ret.extend(group_years[1:])  # Keep the first year in marker.
                    elif not group_years:
                        ret.append(ungroup_years[0])  # Keep first year for title.
                        if len(ungroup_years) > 2:
                            ret.extend(ungroup_years[2:])
        return ret


DATE.rules(KeepMarkedYearInFilepart)
