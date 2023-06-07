UPLOAD_IMAGE = """
**Get a list of contacts whose birthday falls within the selected time period. The period cannot exceed 7 days.**

If the **{from_date}** parameter is not specified, then a list of contacts whose birthday falls within the period
**{to_date} - 7 days** will be returned.

If the **{to_date}** parameter is not specified, then a list of contacts whose birthday falls within the period
**{from_date} + 7 days** will be returned.

If none of the parameters is specified, then a list of contacts whose birthday falls within the next 7 days
from the current one will be returned.

If the period is longer than 7 days, it will be truncated to 7 days from the **{from_date}** parameter.
"""
