"""REST API for posts."""
import flask
import webAPI

@webAPI.app.route('/api/datas/', methods=['GET'])
def create_data():
    """Send latest data to the web."""
    connection = webAPI.model.get_db()
    cur = connection.execute(
        "select * from data "
        "order by created DESC "
        "LIMIT 1 ",
    )
    data = cur.fetchone()

    if not data:
        return flask.jsonify({'message': 'No data found'}), 404
    
    total_carbon_emission = data['totalCarbonEmission'] # total_baseline_emissions
    solar_carbon_emission = data['solarCarbonEmission'] # solar_saving
    ev_carbon_emission = data['evCarbonEmission'] # ev_emission_reduction
    ems_carbon_emissions = data['emsCarbonEmission'] # total_emission_reduction

    impact_data = {
        'total_carbon_emission': total_carbon_emission + ' lbs',
        'solar_carbon_emission': solar_carbon_emission + ' lbs',
        'ev_carbon_emission': ev_carbon_emission + ' lbs',
        'ems_carbon_emissions': ems_carbon_emissions + ' lbs'
    }

    net_inverter_grid = data['netInvertertoGrid']
    net_solar_inverter = data['netSolartoInverter']
    net_inverter_components = data['netInvertertoComps']

    energy_flow = {
        'net_inverter_to_grid': net_inverter_grid + ' kw',
        'net_solar_to_inverter': net_solar_inverter + ' kw', # pv_output
        'net_inverter_to_components': net_inverter_components + ' kw'
    }

    # total_power_consumed = data['totalPowerConsumed']
    # total_clean_consumed = data['totalCleanConsumed']
    # total_grid_consumed = data['totalGridConsumed']
    # total_solar_consumed = data['totalSolarConsumed']

    # pie_chart = {
    #     'total_power_consumed': total_power_consumed + ' kw',
    #     'total_clean_consumed': total_clean_consumed + ' kw',
    #     'total_grid_consumed': total_grid_consumed + ' kw',
    #     'total_solar_consumed': total_solar_consumed + ' kw'
    # }

    # context = {
    #     'impact_data': impact_data,
    #     'energy_flow': energy_flow,
    #     'pie_chart': pie_chart
    # }

    cur = connection.execute(
        "select * from chart "
        "order by created DESC "
        "where created >= DATETIME('now', '-1 year') ",
    )
    lines = cur.fetchall()
    line_data = []
    
    for row in lines:
        baseline_emission = row['baselineEmission']
        emission_without_ems = row['noEMSEmission']
        emission_with_ems = row['withEMSEmission']
        created = row['created']

        point = {
            'baseline_emission': baseline_emission,
            'emission_without_ems': emission_without_ems,
            'emission_with_ems': emission_with_ems,
            'created_time': created
        }
        line_data.append(point)

    context = {
        'impact_data': impact_data,
        'energy_flow': energy_flow,
        'line_data': line_data
    }
    # for row in data:
    #     ems_carbon_emissions = row['emsCarbonEmission']
    #     nonems_carbon_emission = row['nonemsCarbonEmission']
    #     postid = row['postid']
    #     created = row['created']

    #     post = {
    #         'ems_carbon_emissions': ems_carbon_emissions,
    #         'nonems_carbon_emission': nonems_carbon_emission,
    #         'postid': postid,
    #         'created': created
    #     }
    #     context.append(post)
    
    return flask.jsonify(**context), 201