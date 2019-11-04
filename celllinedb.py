import logging
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Ellipse, Polygon, Circle


def main():
    """
    The main function executing all the steps
    Args:
        None
    Returns:
        None
    """
    
    # init the logging
    logging.basicConfig(format='%(asctime)s|%(levelname)s| %(message)s', level=logging.INFO)
    logging.info('Starting celllinedb processing')
    
    # execulte all steps
    conf = read_conf()
    df = read_data(conf)
    df = clean_data(conf, df)
    draw_pdf(conf, df)
    
    logging.info('Finished celllinedb processing')


def read_conf():
    """
    Read in the configuration parameters.
    Args:
        None
    Returns:
        conf (dict): a dictionnary holding all the configurable parameters
    """
    
    
    logging.info("Reading in config")
    with open('config.txt', 'r') as conf_file:
        conf = json.load(conf_file)

    return conf
    
    
def read_data(conf):
    """
    Reads in the excel file database.
    Args:
        conf (dict): a dictionnary holding all the configurable parameters
    Returns:
        df (DataFrame): a DataFrame holding the database
    """
    
    logging.info("Reading in data")
    
    df = pd.read_excel(conf['main']['db_path'], 'DATABASE')
    df = df.dropna(0, 'all')
    df = df.loc[:, ['Tiroir', 'Position', 'Name', 'Date_congel', 'Organism', 'Tissue', 'Disease']]
    df.columns = ['drawer', 'pos', 'name', 'date', 'organism', 'tissue', 'disease']
    
    return df

    
def clean_data(conf, df):
    """
    Cleans the data to make consensus on the organisms, tissues and diseases columns
    Args:
        conf (dict): a dictionnary holding all the configurable parameters
        df (DataFrame): the DataFrame holding the database
    Returns:
        df (DataFrame): the *cleaned* DataFrame holding the database
    """
    
    logging.info("Cleaning data")
        
    # go through each category
    categories = ['organism', 'disease', 'tissue']
    for category in categories:
    
        # get the list of keys for this category (like "human", "mouse", etc. for category "organism")
        category_keys = conf['clean'][category]
        # store the indices of all matched rows
        matched_rows_indices = []
        
        # go through each key
        for category_key in category_keys:
        
            # get the list of patterns for the current key (like "mouse" or
            #    "musmusculus" for key "mouse" in category "organism")
            patterns = conf['clean'][category][category_key]
            
            # go through each pattern
            for pattern in patterns:
            
                # create the actual pattern
                pattern = ('.*' + pattern + '.*').replace('.*.*.*', '.*')
                # match the pattern to a lower case, cleaned version of the value of each row
                matching_rows = df[category].str.replace('[-_^ ()]', '').str.match(pattern, case=False)
                # consider badly matched rows (None or NaN) as non-matching
                matching_rows[matching_rows.isnull()] = False
                # store the list of matched indices
                matched_rows_indices.extend(matching_rows[matching_rows].index)
                
                # if there was any match
                if matching_rows.sum() > 0:
                    logging.debug('Category "{:8s}": found {:3d} rows matching "{}"'.format(
                        category, matching_rows.sum(), category_key))
                    # overwrite the value in the rows with the key
                    df.loc[matching_rows, category] = category_key
                    
        # replace all unmatched rows with the "unknown" string
        df.loc[~df.index.isin(matched_rows_indices), category] = 'unknown'
        logging.debug('Category "{:8s}": found {:3d} rows without match (set to "unknown")'.format(
            category, len(df[df[category] == 'unknown'])))

    return df


def draw_pdf(conf, df):
    """
    Initializes the PDF file and draws one page per drawer.
    Args:
        conf (dict): a dictionnary holding all the configurable parameters
        df (DataFrame): the DataFrame holding the database
    Returns:
        None
    """
    
    # get the maximum number of drawers
    n_drawers = int(max(df['drawer']))
    
    # load the CHUV logo
    conf['draw']['chuv_logo'] = plt.imread(conf['draw']['logo_path'])
    
    # initialize the pdf file and get page size
    logging.info("Initializing the canvas of the PDF file")
    with PdfPages(conf['main']['output_pdf_file_path']) as pdf:
    
        # create a page for each drawer
        logging.info("Drawing pages")
        for i_drawer in range(1, n_drawers + 1):
            draw_page(conf, df, pdf, i_drawer)

    
def draw_page(conf, df, pdf, i_drawer):
    """
    Draws one page for the specified drawer.
    Args:
        conf (dict): a dictionnary holding all the configurable parameters
        df (DataFrame): the DataFrame holding the database
        pdf (PdfPages): the PdfPages object
        i_drawer (int): the current drawer index
    Returns:
        None
    """

    logging.info("Drawing page {}".format(i_drawer))
    
    # extract the relevant configuration section
    draw_conf = conf['draw']
    
    # create a matplotlib figure with the right aspect ratio
    fig = plt.figure(figsize=[7, 10])
    
    # re-position the axe and remove borders
    ax = plt.gca()
    ax.set_position([0.05, 0.05, 0.95, 0.9])
    plt.axis('off')

    ## draw the header information
    logging.info("Drawing header")
    
    # add drawer information
    y = 1.01
    plt.text(0, 1.01, r'$\bf{Tiroir}$ ' + str(i_drawer), fontsize=draw_conf['fontsize']['header1'])
        
    # add the current date
    y -= 0.04
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    plt.text(0, 0.97, r'$\bf{Date}$: ' + now_str, fontsize=draw_conf['fontsize']['header2'])
    
    # add the database file's path
    plt.text(-0.02, -0.03, r'$\bf{Chemin\ du\ fichier\ Excel}$:' + conf['main']['db_path'], fontsize=draw_conf['fontsize']['footer'])
    
    # draw a base triangle-like polygon
    logging.info("Drawing base shape")
    poly_conf = draw_conf['poly']
    poly_coords = [poly_conf[c] for c in ['bot_left', 'top_left', 'top_right', 'bot_right']]
    polygon = Polygon(poly_coords, True, facecolor=poly_conf['color'])
    ax.add_patch(polygon)
    
    # draw an ellipse at the bottom
    ell_conf = draw_conf['ellipse']
    arc = Ellipse(ell_conf['center'], ell_conf['width'], ell_conf['height'], facecolor=ell_conf['color'])
    ax.add_patch(arc)

    # go row by row
    logging.info("Drawing circles and their content")
    for i_row in range(11):
        # go through each column, whith always more circles on each row
        n_circles = i_row + 2
        for i_col in range(n_circles):
            # draw the current circle
            draw_circle(conf, df, ax, i_drawer, i_row, i_col, n_circles)

    # add the CHUV logo and the departement name
    plt.text(0.98, 0.96, 'Service de médecine', horizontalalignment='right',
        fontsize=draw_conf['fontsize']['header2'])
    plt.text(0.98, 0.94, 'nucléaire et imagerie', horizontalalignment='right',
        fontsize=draw_conf['fontsize']['header2'])
    plt.text(0.98, 0.92, 'moléculaire', horizontalalignment='right',
        fontsize=draw_conf['fontsize']['header2'])
    # create separate axes for the logo
    logo_ax = fig.add_axes([0.82, 0.92, 0.150, 0.08], frameon=False)
    logo_ax.imshow(conf['draw']['chuv_logo'])
    plt.axis('off')
    
    # save the current figure to a page page
    pdf.savefig()
    plt.close()
    
    
def draw_circle(conf, df, ax, i_drawer, i_row, i_col, n_circles):
    """
    Draws a single circle for the specified drawer, row and column (circle).
    Args:
        conf (dict): a dictionnary holding all the configurable parameters
        df (DataFrame): the DataFrame holding the database
        ax (Axes): the current axis object
        i_drawer (int): the current drawer's index
        i_row (int): the current row's index
        i_col (int): the current column's index
        n_circles (int): the number of circles in the current row
    Returns:
        None
    """
    # extract the relevant configuration section
    cir_conf = conf['draw']['circle']
    font_conf = conf['draw']['fontsize']
    
    conf['draw']['label_params']['fontsize'] = font_conf['side_label']
    
    # define the coordinates of the current circle's center
    x = cir_conf['top_left'][0] + i_col * (cir_conf['diameter'] + cir_conf['pad'][0]) - i_row * cir_conf['x_shift']
    y = cir_conf['top_left'][1] - i_row * (cir_conf['diameter'] + cir_conf['pad'][1])
    
    # draw the first "column" (circle number) label
    if i_col == 0 and i_row == 0:
        plt.arrow(x + 0.03, y + 0.09, -0.01, -0.02, **conf['draw']['arrow_params'])
        plt.text(x + 0.03, y + 0.10, str(i_col + 1), **conf['draw']['label_params'])
        
    # draw the "column" (circle number) labels
    if i_col == n_circles - 1 and i_row < 10:
        plt.arrow(x + 0.04, y + 0.08, -0.01, -0.02, **conf['draw']['arrow_params'])
        plt.text(x + 0.04, y + 0.09, str(i_col + 1), **conf['draw']['label_params'])
    
    # draw the row number labels
    if i_col == 0:
        # last row should be slightly shifted to the right
        if i_row == 10:
            plt.text(x - 0.05, y - 0.01, conf['draw']['letters'][i_row] + ' →', **conf['draw']['label_params'])
        else:
            plt.text(x - 0.12, y - 0.01, conf['draw']['letters'][i_row] + ' →', **conf['draw']['label_params'])
        
    # last row is special as it has only 4 circles
    if i_row == 10:
        valid_indices = [3, 4, 7, 8]
        # if we are not in the circles to be displayed, skip processing
        if i_col not in valid_indices: return
        # re-map indices for last row
        i_col = valid_indices.index(i_col)
    
    # fetch the right column of the database
    df_row = df.query('drawer == {} & pos == "{}{}"'.format(i_drawer, conf['draw']['letters'][i_row], i_col + 1))
    
    # if no result or empty name field, leave the circle empty (white)
    if len(df_row) == 0 or len(df_row) == 1 and str(df_row.iloc[0]['name']) == 'nan':
        logging.info('Nothing at D{}-{}{}'.format(i_drawer, conf['draw']['letters'][i_row], i_col + 1))
        circle_color = 'white'
        
    # if more than one result
    elif len(df_row) > 1:
        logging.error('ERROR: multiple matches ({}) at D{}-{}{}'.format(len(df_row), i_drawer,
            conf['draw']['letters'][i_row], i_col + 1))
        circle_color = 'red'
    
    # a single item was found, display the content into the circle
    elif len(df_row) == 1:
        # fetch the name and the date
        name = df_row.iloc[0]['name']
        date = df_row.iloc[0]['date']
        # convert datetime objects to string
        if isinstance(date, datetime): date = date.strftime('%d-%m-%y')
        logging.debug('Found {} ({}) at D{}-{}{}'.format(name, date, i_drawer,
            conf['draw']['letters'][i_row], i_col + 1))

        # write the content to the circle's center
        plt.text(x, y + 0.01, name, fontsize=font_conf['circle_name'], horizontalalignment='center')
        plt.text(x, y - 0.01, date, fontsize=font_conf['circle_date'], horizontalalignment='center')
        
        circle_color = [0.9, 0.9, 0.9]
      
    # draw the current circle
    circ = Ellipse([x, y], cir_conf['diameter'], cir_conf['diameter'], linewidth=2, facecolor=circle_color)
    ax.add_patch(circ)
    
    
# call main() if this script is executed
if __name__ == '__main__':
    main()