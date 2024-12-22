from convertdate import hebrew

from tqdm import tqdm
import statistics
import shelve
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

gregorian_start = datetime.date(1582, 10, 15)
days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def date_iterator(start_date, end_date):
    """
    creates an iterator yielding dates from start_date to end_date, inclusive.

    Args:
        start_date (datetime.date)
        end_date (datetime.date)

    Yields:
        datetime.date: The next date in the range from start_date to end_date.
    """
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += datetime.timedelta(days=1)


def thanksgiving_gregorian_date(year):
    """
    Calculate the Gregorian date of Thanksgiving for a given year in the United States according to
    information on the varying date provided by the National Archives:
    https://prologue.blogs.archives.gov/2023/11/20/thanksgiving-as-a-federal-holiday/

    Args:
        year (int): The year for which to calculate Thanksgiving.

    Returns:
        datetime.date: The Gregorian date of Thanksgiving for the given year, or None
                       for years prior to the 1863 presidential proclamation.
    """
    thanksgiving = None
    with shelve.open('thanks_giving_dates') as shelf:  # cache results
        if str(year) in shelf:
            return shelf[str(year)]
        else:
            first_november = datetime.date(year, 11, 1)
            last_november_day = datetime.date(year, 11, 30)
            first_thursday = first_november + datetime.timedelta(days=(3 - first_november.weekday() + 7) % 7)
            if year < 1863:
                # Ignoring years prior to 1863, where it was celebrated in various spring and autumn months
                thanksgiving = None
            elif year >= 1863 and year < 1941 and year != 1865:
                # Starting with the Oct 3, 1863 presidential proclomation by Abraham Lincolna proclaimed
                # setting Thanksgiving to be celebrated on the last Thursday of November
                last_thursday = last_november_day - datetime.timedelta(days=(last_november_day.weekday() - 3) % 7)
                thanksgiving = last_thursday
            elif year == 1865:
                # following Lincoln's assassination, President Andrew Johnson declared Thanksgiving to
                # be celebrated on the first Thursday in December
                first_december = datetime.date(year, 12, 1)
                first_thursday_dec = first_december + datetime.timedelta(days=(3 - first_december.weekday() + 7) % 7)
                thanksgiving = first_thursday_dec
            elif year >= 1941 or year == 1933:
                # Roosevelt, concerned that the shortened Christmas shopping season might dampen the economic recovery,
                # moved Thanksgiving a week earlier
                third_thursday = first_thursday + datetime.timedelta(weeks=3)
                thanksgiving = third_thursday
            elif year >= 1939 or year < 1941:
                second_thursday = first_thursday + datetime.timedelta(weeks=2)
                thanksgiving = second_thursday
            elif year >= 1863:
                raise ValueError(f"Thanksgiving date not defined for {year}")
            shelf[str(year)] = thanksgiving
    return thanksgiving


def hanukkah_gregorian_date(gregorian_year):
    """
    Calculate the dates on the Gregorian calendar of Hanukkah for a given year.

    Args:
        gregorian_year (int): The year on the gregorian calendar to calculate when Hanukkah falls.

    Returns:
        list: A list of `datetime.date` objects representing the date(s) of Hanukkah in the given Gregorian year.

    Raises:
        ValueError: If the Gregorian year is before 1582, when the Gregorian calendar was introduced.

    Notes:
        - Shelve is used to cache results for faster subsequent lookups.
        - Hanukkah starts on the 25th day of Kislev in the Hebrew calendar.
        - For years after 3030, Hanukkah may fall entirely in the next Gregorian year, those years
          without a Hanukkah return an empty list
    """
    result = []
    key = str(gregorian_year)
    if gregorian_year < 1582:
        raise ValueError("Gregorian calendar began on October 15, 1582")
    with shelve.open('hanukkah_dates') as shelf:  # cache results
        if key in shelf:
            result = shelf[key]
        else:
            for date_gregorian in date_iterator(datetime.date(gregorian_year, 1, 1),
                                                datetime.date(gregorian_year, 12, 31)):
                # look across entire gregorian year
                date_hebrew = hebrew.from_gregorian(date_gregorian.year, date_gregorian.month, date_gregorian.day)
                if date_hebrew[1] == 9 and date_hebrew[2] == 25:
                    result.append(date_gregorian)
            shelf[key] = result
    return result


def notable_hanukkah_years(year=None, limit=1000):
    """
    Calculate notable years for Hanukkah in relation to Chrristmas and Thanksgiving.

    Args:
        year (int, optional): The starting year for the calculation. Defaults to the current year.
        limit (int, optional): Span of years to consider. Defaults to 1000

    Returns:
        dict: A dictionary containing notable years and their occurrences:
            - 'christmas_eve': List of years when Hanukkah begins on Christmas Eve.
            - 'christmas_day': List of years when Hanukkah begins on Christmas Day.
            - 'thanksgiving': List of years when Hanukkah begins on Thanksgiving.
            - 'thanksgiving_eve': List of years when Hanukkah ends on Thanksgiving.
            - 'no_hanukkah': List of years when Hanukkah fall in the Gregorian year.
            - 'by_date': Dictionary with dates (MM-DD) as keys and lists of years as values.
            - 'by_dow': Dictionary with days of the week as keys and lists of years as values.
            - 'start_year': The starting year of the calculation.
            - 'end_year': The ending year of the calculation.
    """
    if year is None:
        year = datetime.datetime.now().year

    # place start year in the middle of the range, limited by the gregorian calendar
    start_year = max(year - round(limit / 2), gregorian_start.year)
    end_year = start_year + limit

    result = {'christmas_eve': [], 'christmas_day': [],
              'no_hanukkah': [],
              'thanksgiving': [],
              'thanksgiving_eve': [],
              'by_date': {key.strftime("%m-%d"): [] for key in
                          date_iterator(datetime.date(2024, 11, 15), datetime.date(2025, 1, 31))},
              'by_dow': {key: [] for key in days_of_week},
              'start_year': start_year, 'end_year': end_year}

    for year in tqdm(range(start_year, end_year)):
        hanukkah_dates = hanukkah_gregorian_date(year)  # date (or dates after 3030) of Hanukkah in that calendar year
        thanksgiving_date = thanksgiving_gregorian_date(year)
        if thanksgiving_date is not None:
            thanksgiving_eve_date = thanksgiving_date + datetime.timedelta(days=1)
        else:
            thanksgiving_eve_date = None
        if len(hanukkah_dates) < 0:
            raise ValueError(f"negative count of Hanukkah dates for {year}, this should not happen.")
        elif len(hanukkah_dates) == 0:
            # beginning in 3031, differences in the Jewish and Gregorian calendars have accumulated to a level that
            # pushes Hanukkah into the next calendar year
            result['no_hanukkah'].append(year)
        else:
            # one or more Hanukkahs found this calendar year
            for date in hanukkah_dates:

                # Christmas coincidences
                if date.month == 12:
                    if date.day == 26:  # Hannukah celebrations start the night before
                        result['christmas_day'].append(year)
                    if date.day == 25:
                        result['christmas_eve'].append(year)
                # Thanksgiving
                if thanksgiving_date is not None:
                    if date.month == thanksgiving_date.month and date.day == thanksgiving_date.day:
                        result['thanksgiving'].append(year)
                    if date.month == thanksgiving_eve_date.month and date.day == thanksgiving_eve_date.day:
                        result['thanksgiving_eve'].append(year)

                # distribution of dates and days of the week
                result['by_date'][date.strftime("%m-%d")].append(year)
                result['by_dow'][date.strftime("%A")].append(year)

    # match search direction
    return result


def calculate_delta_mean(input_list):
    """
    Calculate the differences between consecutive elements in a list and their mean.

    Args:
        input_list (list of int or float): A list of numerical values.

    Returns:
        tuple: A tuple containing:
            - deltas (list of int or float): A list of differences between consecutive elements.
            - mean (float): The mean of the differences.

    Raises:
        ValueError: If the input list has fewer than 2 elements.
    """
    if len(input_list) < 2:
        raise ValueError("Input list must contain at least two elements.")
    deltas = [input_list[i + 1] - input_list[i] for i in range(len(input_list) - 1)]
    mean = statistics.mean(deltas)
    return deltas, mean


def plot_date_distribution(d):
    """
    Plot the distribution of Hanukkah start dates by specific dates.

    Args:
        d (dict): A dictionary where keys are dates (in "MM-DD" format) and values are lists of years when Hanukkah starts on that date.

    Returns:
        None: This function saves the plot as 'hanukkah_dates.png'.

    """
    dates = []
    counts = []
    colors = []

    for date in date_iterator(datetime.date(2024, 11, 20), datetime.date(2025, 1, 5)):
        dates.append(date)
        key = date.strftime("%m-%d")
        counts.append(len(d[key]))
        if key == "12-25":
            colors.append('red')
        elif key == "12-24":
            colors.append('green')
        else:
            colors.append('blue')

    fig, ax = plt.subplots(figsize=(16, 9))  # Set the desired aspect ratio

    plt.bar(dates, counts, color=colors, width=0.8)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, fontsize=36)  # Set the font size here
    plt.tight_layout()
    plt.gca().yaxis.set_visible(False)

    # Turn off splines
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.savefig('hanukkah_dates.png')


def plot_dow_distribution(d):
    """
    Plot the distribution of Hanukkah start dates by day of the week.

    Args:
        d (dict): A dictionary where keys are days of the week and values are lists of years when Hanukkah starts on that day.

    Returns:
        None: This function saves the plot as 'hanukkah_dows.png'.

    """
    dows = []
    counts = []
    for dow in days_of_week:
        dows.append(dow)
        if dow in d:
            counts.append(len(d[dow]))
        else:
            counts.append(0)

    plt.figure(figsize=(16, 9))
    plt.bar(range(0, len(dows)), counts, color='lightblue')
    plt.xticks(range(0, len(dows)), dows)

    plt.xticks(rotation=45, fontsize=36)  # Set the font size here
    plt.tight_layout()
    plt.gca().yaxis.set_visible(False)

    # Turn off splines
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.savefig('hanukkah_dows.png')


def main(total_years=2000):
    current_year = datetime.datetime.now().year

    print(f"Hanukkah coincidence as of {current_year}\n")
    notable = notable_hanukkah_years(limit=total_years)
    notable['thanksgiving_any'] = notable['thanksgiving'] + notable['thanksgiving_eve']
    notable['thanksgiving_any'].sort()
    notable['christmas'] = list(set(notable['christmas_day'] + notable['christmas_eve']))
    notable['christmas'].sort()

    for label, the_list in zip(['Start on Christmas day', 'Start on Christmas eve', 'overlap Christmas',
                                'No Hanukkah', 'overlap Thanksgiving'],
                               [notable['christmas_day'], notable['christmas_eve'], notable['christmas'],
                                notable['no_hanukkah'], notable['thanksgiving_any']]):
        if len(the_list) >= 2:
            deltas, mean = calculate_delta_mean(the_list)
        else:
            mean = -1
        last = [x for x in the_list if x < current_year]
        next = [x for x in the_list if x > current_year]
        print(f"{100 * (len(the_list) / 2000):.2f}% {label}:")
        if len(last) > 0:
            print(f" last in {last[-1]},", end='')
        else:
            print(f" hasn't happened since at least {notable['start_year']}", end='')
        if len(next) > 0:
            print(f" next in {next[0]}")
        else:
            print(f" and wont happen again through at least {notable['end_year']}")
        if len(last) > 0:
            print(f" happened {len(last)} times since the year {notable['start_year']}")
        print(f" separated by {round(mean)} years on average (between {min(the_list)} and {max(the_list)})")
        print(f" in these years: {", ".join([str(item) for item in the_list])}")
        print()

    # create charts of Hanukkahs by date and day of the week
    plot_date_distribution(notable['by_date'])
    plot_dow_distribution(notable['by_dow'])


if __name__ == '__main__':
    main()
