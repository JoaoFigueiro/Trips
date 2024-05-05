from flask import Flask, render_template, request
import duckdb

app = Flask(__name__)

def install_spatial():
    duckdb.execute("INSTALL spatial;")
    duckdb.execute("LOAD spatial;")


@app.route('/', methods=['GET', 'POST'])
def grouped_trips():
    file_path = "trips_1.csv"

    region = request.form.get('regionInput')
    bounding_box = request.form.get('boundingBox')
    
    #cleaning filters
    if region == '': 
        region = None 

    if bounding_box == '':
        bounding_box = None

    filter = None

    if region: 
        filter = f"""
        WHERE
            LOWER(region) = TRIM(LOWER('{region}'))
        """

    if bounding_box: 
        xmin, ymin, xmax, ymax = bounding_box.split()
        bounding_box_coords = [(xmin, ymin), (xmax, ymax)]

        x_values = [coord[0] for coord in bounding_box_coords]
        y_values = [coord[1] for coord in bounding_box_coords]

        xmin = min(x_values)
        ymin = min(y_values)
        xmax = max(x_values)
        ymax = max(y_values)

        filter = f"""
        WHERE
            ST_WITHIN(ST_GeomFromText(origin_coord), 
                ST_GeomFromText(
                    'POLYGON(
                        (
                            {xmin} {ymin}, 
                            {xmax} {ymin}, 
                            {xmax} {ymax}, 
                            {xmin} {ymax}, 
                            {xmin} {ymin}
                        )
                    )'
                )
            )
            OR ST_WITHIN(ST_GeomFromText(destination_coord), 
                ST_GeomFromText(
                    'POLYGON(
                        (
                            {xmin} {ymin}, 
                            {xmax} {ymin}, 
                            {xmax} {ymax}, 
                            {xmin} {ymax}, 
                            {xmin} {ymin}
                        )
                    )'
                )
            ) 
        """     
    
    if region and bounding_box: 
        filter += f" OR LOWER(region) = TRIM(LOWER('{region}'))"

    query = f"""
    SELECT
        region, 
        ST_AsText(ST_Union_Agg(ST_GeomFromText(origin_coord))) AS origin_coord,
        ST_AsText(ST_Union_Agg(ST_GeomFromText(destination_coord))) AS destination_coord,
        DATE_TRUNC('day', datetime) AS time_window
    FROM
        {file_path}
    {filter}
    GROUP BY
        region,
        DATE_TRUNC('day', datetime)
    ORDER BY
        region, 
        time_window
    LIMIT 100
    """

    count_query = f"""
    WITH main_query AS ( 
    {query}
    ), weekly_trips AS ( 
    SELECT
        WEEK(time_window) as week,
        COUNT(*) AS weekly_trips 
    FROM 
        main_query 
    GROUP BY 
        WEEK(time_window)
    )
    SELECT
        ROUND(MEAN(weekly_trips)) AS average_weekly_trips
    FROM
        weekly_trips;
    """

    duckdb.sql(f"CREATE TABLE IF NOT EXISTS trips AS {query}")
    
    result = duckdb.query(query).to_df()
    result = result.to_dict(orient='records')

    weekly_average = duckdb.query(count_query)
    weekly_average = weekly_average.fetchone()[0]

    duckdb.sql(f"CREATE TABLE IF NOT EXISTS weekly_average AS SELECT {weekly_average}")

    return render_template('trips.html', trips=result, weekly_average=weekly_average)


if __name__ == '__main__':
    install_spatial()

    duckdb.sql("CREATE TABLE seed_trips AS SELECT * FROM 'trips_1.csv'");

    app.run(debug=True)
