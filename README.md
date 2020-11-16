# notion-to-ics

Export your Notion calendar to importable, categorized ICS files

## Introduction

This simple Python script allows to automatically generate ICS files from a Notion calendar, sorted by categories. A
**category** must be a _multi-select property_ that you use to categorize your calendar entries.

> If you do not have this property, don't worry -- simply set `categories_property` to anything

For each category, a `calendar_<category-name>.ics` file will be generated.

## Parameters

You can customize the export with the following parameters, which you can set in the `to_ics.py` script:

| Parameter | Description |
| --- | --- |
| `settings` | `token`: the Notion `token_v2` cookie (see _How to retrieve `token_v2` cookie_ below for more information on how to obtain it)<br>`calendar_url`: the full Notion calendar URL |
| `categories_property` | The name of the **multi-select** property that you will use to categorize your calendar entries |
| `categories_list` | A list of category names that you want to sort your calendar entries by. The last item must be the name entries that cannot be sorted into the previous category will be grouped upon (i.e., if it's `Others`, the entries that cannot be categorized on the previous ones will fall into `calendar_Others.ics`). There must be at least this last item in the list. |
| `show_others` | Whether you want to prepend the other categories in the event names. For example, if you group by `Category A` but your property contains `Category A1` and `Category A2`, the event will be listed under `calendar_Category A.ics` with title `[Category A1, Category A2] <name-of-event>` |
| `export_route` | Route the files will be exported to |

Feel free to tweak the code as much as you want to!

##### How to retrieve `token_v2` cookie

In Chrome, enter any Notion page and open the element inspector (F12). Then, enter Application > Storage > Cookies and find and copy the `token_v2` cookie.

## Deployment suggestions

If you have a public server, you can schedule jobs and expose your `.ics` files so that you can import them in any service such as Google Calendar. I suggest you to use `cron` to schedule jobs.

As you might have used a Python `venv` to install requierements, you can add the following line to `crontab`:

```
<frequency> <route-to-venv>/bin/python3 <route-to-repo>/to_ics.py
```

## Common issues

If you get the following error:

```
Traceback (most recent call last):
  File "to_ics.py", line 162, in <module>
    cals = get_icals(client, settings['calendar_url'], categories_property, categories_list)
  File "to_ics.py", line 87, in get_icals
    calendar_query = calendar_view.build_query()
  File "<route-to-venv>/lib/python3.8/site-packages/notion/collection.py", line 248, in build_query
    calendar_by = self._client.get_record_data("collection_view", self._id)[
KeyError: 'query'
```

Simply modify the `notion/collection.py` file from the `notion` package. Search this lines:

```python
class CalendarView(CollectionView):

    _type = "calendar"

    def build_query(self, **kwargs):
        calendar_by = self._client.get_record_data("collection_view", self._id)[
            "query"
        ]["calendar_by"]
        return super().build_query(calendar_by=calendar_by, **kwargs)
```

and change them to:

```python
class CalendarView(CollectionView):

    _type = "calendar"

    def build_query(self, **kwargs):
        calendar_by = self._client.get_record_data("collection_view", self._id)[
            "query2"    # change "query" to "query2"
        ]["calendar_by"]
        return super().build_query(calendar_by=calendar_by, **kwargs)
```

## Credit

Based on [evertheylen/notion-export-ics](https://github.com/evertheylen/notion-export-ics).