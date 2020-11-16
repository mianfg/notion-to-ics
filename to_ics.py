#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
notion-to-ics
=============
Export your Notion calendar to importable, categorized ICS files
"""

__author__      = "Miguel Ángel Fernández Gutiérrez (@mianfg)"
__copyright__   = "Copyright 2020, @mianfg"
__credits__     = ["Miguel Ángel Fernández Gutiérrez"]
__license__     = "Creative Commons Zero v1.0 Universal"
__version__     = "1.0"
__mantainer__   = "Miguel Ángel Fernández Gutiérrez"
__email__       = "hello@mianfg.me"
__status__      = "Production"



import json, sys, os
from datetime import datetime

from notion.client import NotionClient
from notion.collection import CalendarView
from notion.block import BasicBlock
from notion.user import User

from icalendar import Calendar, Event

"""
Client settings
---------------
token:          Notion token_v2 cookie
calendar_url:   Full Notion calendar URL
"""
settings = {
    'token':        '',
    'calendar_url': ''
}

"""
Categories property
-------------------
Name of the property that categorizes calendar entries
"""
categories_property = "tag"

"""
Categories tree
---------------
An array containing the categories that will be exported separately.
The last entry must be the name of the "Others" calendar, i.e., the
calendar that will contain the events that cannot be categorized under
the previous categories listed
"""
categories_list = [
    "Other"
]

"""
Show other categories
---------------------
Decide to prepend the other categories to the event title
"""
show_others = True

"""
Export route
------------
Route where the ICS files will be exported
"""
export_route = "."



# Hack some representation stuff into notion-py
BasicBlock.__repr__ = BasicBlock.__str__ = lambda self: self.title
User.__repr__ = User.__str__ = lambda self: self.given_name or self.family_name

def get_icals(client, calendar_url, categories_property, categories_list, show_others):
    calendar = client.get_block(calendar_url)

    for view in calendar.views:
        if isinstance(view, CalendarView):
            calendar_view = view
            break
    else:
        raise Exception(f"Couldn't find a calendar view in the following list: {calendar.views}")

    calendar_query = calendar_view.build_query()
    calendar_entries = calendar_query.execute()

    collection = calendar.collection
    schema = collection.get_schema_properties()

    properties_by_name = {}
    properties_by_slug = {}
    properties_by_id = {}
    title_prop = None

    for prop in schema:
        name = prop['name']
        if name in properties_by_name:
            print("WARNING: duplicate property with name {}".format(name))
        properties_by_name[name] = prop
        properties_by_slug[prop['slug']] = prop
        properties_by_id[prop['id']] = prop
        if prop['type'] == 'title':
            title_prop = prop
    
    assert title_prop is not None, "Couldn't find a title property"

    dateprop = properties_by_id[calendar_query.calendar_by]

    cals = {}
    for category in categories_list:
        cals[category] = Calendar()
        cals[category].add("summary", "Imported from Notion. Designed by @mianfg")
        cals[category].add('version', '2.0')
    
    for e in calendar_entries:
        date = e.get_property(dateprop['id'])
        if date is None:
            continue
        
        name = e.get_property(title_prop['id'])
        clean_props = {'NAME': name}
        
        # determine calendar
        cal = cals[categories_list[-1]]
        try:
            categories = e.get_property(categories_property)
        except:
            categories = []
        for category in categories:
            if category in categories_list:
                cal = cals[category]
                categories.remove(category)

        # Put in ICS file
        event = Event()
        desc = ''
        event.add('dtstart', date.start)
        if date.end is not None:
            event.add('dtend', date.end)
        desc += '🔗 ' + e.get_browseable_url() + '\n\n'
        desc += '__________\n\n'
        for k, v in e.get_all_properties().items():
            if k != dateprop['slug'] and k != categories_property:
                name = properties_by_slug[k]['name']
                desc += "  - {}: {}\n".format(name, v)
                clean_props[name] = v
        
        title = ""
        if len(categories) > 0 and show_others:
            title += f"[{', '.join(categories)}] "
        title += clean_props[name]

        event.add('summary', title)
        event.add('description', desc)

        cal.add_component(event)    
    return cals

####

client = NotionClient(token_v2=settings['token'], monitor=False)
cals = get_icals(client, settings['calendar_url'], categories_property, categories_list, show_others)

for cal in cals:
    with open(os.path.join(export_route, f'calendar_{cal}.ics'), 'wb') as f:
        f.write(cals[cal].to_ical())
        f.close()
