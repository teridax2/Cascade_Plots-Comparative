# scripts  by Roy Haggerty for WW2100 data vis
#   Modified by Owen Haggerty
# Cascade plots 
#
# February - March, 2014
# June - July, 2014
#
# Python 2.7
# Dependencies & libraries that need to be installed:
#    numpy
#    matplotlib
#    xlrd
#
#  Modified Mar 4 to
#    - add colobar scale
#    - drop purple from colorbar scale
#    - add legend on colorbar
#  Modified Mar 6 to
#    - add box-and-whisker
#    - change colors on bottom plot
#  Modified Mar 10 for csv files
#  Modified Mar 12 for paths and directories
#  Modified Mar 15 for snow, irrigation, precip, ET, potet
#  Modified Mar 20 for metric and std units
#  Modified Jun 9 for automatic update of metadata information, added municipal use &
#    unexercised water rights

########################################################################################
########################################################################################
########################################################################################

def compare(
            Reference_file,             #the name of the reference file
            Compared_file,              #the name of the file to be compared
            title,                      #the title of the graph to be generated
            flood_Q,                    #the level of the flood line
            data_type = 'stream',       #the type of data
            flood_Q_available = False,  #whether the flood level is available
            Display = False,            #whether the graph is to be displayed(True) or saved as a PNG file(False)
            SI = True                   #Whether the units should be changed to metric(False) or left as is(True)
            ):

    """
    Make a cascade plot and associated side & bottom graphs to show time series of discharge
    """
    
    import numpy as np          #imports
    from   pylab import plot, ylim, xlim, show, xlabel, ylabel, grid
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    import matplotlib.cm as cm
    import xlrd
    import matplotlib.dates as dates
    import datetime
    import matplotlib.ticker as ticker
    import matplotlib as mpl
    import comparative_constants as cst   # constants.py contains constants used here
    import math
    import matplotlib.gridspec as gridspec
    from   mpl_toolkits.axes_grid1 import make_axes_locatable
    from pprint import pprint

    np.set_printoptions(precision=3)

    ###############################
    # Read data in from csv files #
    # Modify arrays as needed     #
    ###############################
    file_1_w_path = cst.path + Reference_file
    file_2_w_path = cst.path + Compared_file
    file_model_csv = Reference_file[:]

    data_1 = np.array(np.genfromtxt(file_1_w_path, delimiter=',',skip_header=1))# Read the csv files
    data_2 = np.array(np.genfromtxt(file_2_w_path, delimiter=',',skip_header=1))

    data_v = data_1[:,0]
##    print data_v[:,np.newaxis].shape
    assert len(data_1[0]) == len(data_2[0])
    data_difference = data_2[:,1:] - data_1[:,1:]
    data_v = np.append(data_v[:,np.newaxis], data_difference,axis=1)

##The following reads the type of data (rainfall, snow, stream discharge,etc.) and responds accordingly.
    if data_type == 'stream': # (default)
        time = data_v[:,0]
        data_yr = data_v[:,1]
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = file_model_csv[:-4]
        plot_structure = '3 by 2'
    elif data_type == 'daminWdup':   # This is for dam files with duplicate entries that must be skipped
        time = data_v[0::2,0]
        data_yr = data_v[0::2,3]
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = file_model_csv[:-4] + '_inflow'
        plot_structure = '3 by 2'
    elif data_type == 'damin':
        time = data_v[:,0]
        data_yr = data_v[:,3]
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = file_model_csv[:-4] + '_inflow'
        plot_structure = '3 by 2'
    elif data_type == 'damoutWdup':   # This is for dam files with duplicate entries that must be skipped
        time = data_v[0::2,0]
        data_yr = data_v[0::2,4]
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = file_model_csv[:-4] + '_outflow'
        plot_structure = '3 by 2'
    elif data_type == 'damout':
        time = data_v[:,0]
        data_yr = data_v[:,4]
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = file_model_csv[:-4] + '_outflow'
        plot_structure = '3 by 2'
    elif data_type == 'precipitation' or\
        data_type == 'snow' or\
        data_type == 'et': 
        time = data_v[:,0]
        data_yr = data_v[:,1]
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        graph_name = file_model_csv[:-4] 
        plot_structure = '2 by 2'
    elif data_type == 'irrigation': 
        time = data_v[:,0]
        data_yr = np.add(data_v[:,2], data_v[:,3])
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        graph_name = file_model_csv[:-4] + '_irrigation'
        plot_structure = '2 by 2'
    elif data_type == 'municipal': 
        time = data_v[:,0]
        data_yr = np.add(data_v[:,4], data_v[:,5])
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        graph_name = file_model_csv[:-4] + '_municipal'
        plot_structure = '2 by 2'
    elif data_type == 'water_rights': 
        time = data_v[:,0]
        data_yr = np.add(data_v[:,8], data_v[:,9])
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        graph_name = file_model_csv[:-4] + '_unexercized_water_rights'
        plot_structure = '2 by 2'
    elif data_type == 'temperature':
        time = data_v[:,0]
        data_yr = data_v[:,2]
        if not SI: data_yr = (data_yr-32.0)/cst.F_to_C
        graph_name = file_model_csv[:-4] + '_temperature'
        plot_structure = '3 by 2'
    elif data_type == 'potet':
        time = data_v[:,0]
        data_yr = data_v[:,2]
        if not SI: data_yr = data_yr/cst.in_to_mm
        graph_name = file_model_csv[:-4] + '_pet'
        plot_structure = '2 by 2'
    
        
    time = time[cst.day_of_year_oct1 - 1:] # water year
    data_yr = data_yr[cst.day_of_year_oct1:-(365-cst.day_of_year_oct1)] # water year
    data_length = len(time)
    num_water_yrs = len(time)/365

    if  not data_type == 'temperature':          # If true, then replace max and min in cascade plot
        plot_lower_bound = np.percentile(data_yr,5)
        plot_upper_bound = np.percentile(data_yr,95)
    elif data_type == 'temperature':
        plot_lower_bound = np.percentile(data_yr,5)
        plot_upper_bound = np.percentile(data_yr,97.5)

    time_date = np.array([cst.Jan1_2010 + datetime.timedelta(days=day)
                          for day in time])

    # Convert the data into an array in numpy format, and clip it to +/- 1 sigma for vis.
    data_2D = np.reshape(np.array(data_yr), (-1,365)) #2D matrix of data in numpy format
    data_2D_clipped = np.empty_like(data_2D)
    data_2D_clipped = np.clip(data_2D, plot_lower_bound, plot_upper_bound)

    ##########################################################
    # Assemble the data needed on the right-hand-side plots. #
    # This differs with data_type.                           #
    ##########################################################

    if data_type == 'stream' or \
       data_type == 'daminWdup' or \
       data_type == 'damoutWdup' or \
       data_type == 'damin' or \
       data_type == 'damout':

        Q_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(Q_max[-9:])
        Q_max_decadal = np.reshape(np.append(Q_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_2 = Q_max_decadal
        plot_type_rhs_2 = 'boxplot'
        
        Q_min = [np.amin(data_2D[i,:]) for i in range(num_water_yrs)]  # min discharge
        extra = np.median(Q_min[-9:])
        Q_min_decadal = np.reshape(np.append(Q_min, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = Q_min_decadal
        plot_type_rhs_1 = 'boxplot'

        if SI:
            ylabel2 = '$Daily \, Q$ [m$^{\t{3}}$/s]'
            ylabel4 = '$Discharge (Q)\,$ [m$^{\t{3}}$/s]'
        else:
            ylabel2 = '$Daily \, Q$ [cfs]'
            ylabel4 = '$Discharge (Q)\,$ [cfs]'
            
        
    elif data_type == 'snow':
        swe_apr1 = data_yr[cst.day_of_year_apr1+(365-cst.day_of_year_oct1):data_length:365]
        extra = np.median(swe_apr1[-9:])
        swe_apr1_decadal = np.reshape(np.append(swe_apr1, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = swe_apr1_decadal
        plot_type_rhs_1 = 'boxplot'
        
        if SI:
            ylabel2 = '$Snow \,Water \,Equivalent\,$ [mm]'
            ylabel4 = '$SWE\,$ [mm]'
        else:
            ylabel2 = '$Snow \,Water \,Equivalent\,$ [in]'
            ylabel4 = '$SWE\,$ [in]'

                
    elif data_type == 'irrigation':
        irigation_data = np.array([np.sum(data_yr[i*365:(i+1)*365]) for i in range(89)])
        if SI: irigation_data = irigation_data*86400./1.e6  # convert from m3/s to millions of m3
        if not SI: irigation_data = irigation_data/1.e3  # convert to thousands of ac-ft
        extra = np.median(irigation_data[-9:])
        irigation_data_decadal = np.reshape(np.append(irigation_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = irigation_data_decadal
        plot_type_rhs_1 = 'boxplot'

        if SI:
            ylabel2 = '$Irrigation \,Rate\,$ [m$^3$/s]'
            ylabel4 = '$Irrig \,Rate\,$ [m$^3$/s]'
        else:
            ylabel2 = '$Irrigation \,Rate\,$ [ac-ft/d]'
            ylabel4 = '$Irrig \,Rate\,$ [ac-ft/d]'
        
    elif data_type == 'municipal':
        municipal_data = np.array([np.sum(data_yr[i*365:(i+1)*365]) for i in range(89)])
        if SI: municipal_data = municipal_data*86400./1.e6  # convert from m3/s to millions of m3
        if not SI: municipal_data = municipal_data/1.e3  # convert to thousands of ac-ft
        extra = np.median(municipal_data[-9:])
        municipal_data_decadal = np.reshape(np.append(municipal_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = municipal_data_decadal
        plot_type_rhs_1 = 'boxplot'

        if SI:
            ylabel2 = '$Municipal Use\,$ [m$^3$/s]'
            ylabel4 = '$Mncpl Use\,$ [m$^3$/s]'
        else:
            ylabel2 = '$Municipal Use\,$ [ac-ft/d]'
            ylabel4 = '$Mncpl Use\,$ [ac-ft/d]'
        
    elif data_type == 'water_rights':
        unusedWR_data = np.array([np.sum(data_yr[i*365:(i+1)*365]) for i in range(89)])
        if SI: unusedWR_data = unusedWR_data*86400./1.e6  # convert from m3/s to millions of m3
        if not SI: unusedWR_data = unusedWR_data/1.e3  # convert to thousands of ac-ft
        extra = np.median(unusedWR_data[-9:])
        unusedWR_data_decadal = np.reshape(np.append(unusedWR_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = unusedWR_data_decadal
        plot_type_rhs_1 = 'boxplot'

        if SI:
            ylabel2 = '$Unxczd \,Water \,Rights\,$ [m$^3$/s]'
            ylabel4 = '$Unxczd \,Wtr \,Rt\,$ [m$^3$/s]'
        else:
            ylabel2 = '$Unxczd \,Water \,Rights\,$ [ac-ft/d]'
            ylabel4 = '$Unxczd \,Wtr \,Rt\,$ [ac-ft/d]'

    elif data_type == 'precipitation':
        precip_data = [np.sum(data_yr[i*365:(i+1)*365]) for i in range(89)]
        extra = np.median(precip_data[-9:])
        precip_data_decadal = np.reshape(np.append(precip_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = precip_data_decadal
        plot_type_rhs_1 = 'boxplot'
        
        if SI:
            ylabel2 = '$Precipitation\,$ [mm/d]'
            ylabel4 = '$Precip\,$ [mm/d]'
        else:           
            ylabel2 = '$Precipitation\,$ [in/d]'
            ylabel4 = '$Precip\,$ [in/d]'
        
    elif data_type == 'temperature':
        T_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(T_max[-9:])
        T_max_decadal = np.reshape(np.append(T_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_2 = T_max_decadal
        plot_type_rhs_2 = 'boxplot'
        
        T_min = [np.amin(data_2D[i,:]) for i in range(num_water_yrs)]  # min discharge
        extra = np.median(T_min[-9:])
        T_min_decadal = np.reshape(np.append(T_min, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = T_min_decadal
        plot_type_rhs_1 = 'boxplot'

        if SI:
            ylabel2 = '$Temperature\,$ [$^{\circ}\mathrm{C}$]'
            ylabel4 = '$Temperature\,$ [$^{\circ}\mathrm{C}$]'
        else:
            ylabel2 = '$Temperature\,$ [$^{\circ}\mathrm{F}$]'
            ylabel4 = '$Temperature\,$ [$^{\circ}\mathrm{F}$]'            
        
    elif data_type == 'et':
        et_data = [np.sum(data_yr[i*365:(i+1)*365]) for i in range(89)]
        extra = np.median(et_data[-9:])
        et_data_decadal = np.reshape(np.append(et_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = et_data_decadal
        plot_type_rhs_1 = 'boxplot'
        
        if SI:
            ylabel2 = '$Evapotranspiration\,$ [mm/d]'
            ylabel4 = '$ET\,$ [mm/d]'
        else:
            ylabel2 = '$Evapotranspiration\,$ [in/d]'
            ylabel4 = '$ET\,$ [in/d]'

    elif data_type == 'potet':
        potet_data = [np.sum(data_yr[i*365:(i+1)*365]) for i in range(89)]
        extra = np.median(potet_data[-9:])
        et_data_decadal = np.reshape(np.append(potet_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = et_data_decadal
        plot_type_rhs_1 = 'boxplot'
        
        if SI:
            ylabel2 = '$Potential Evapotranspiration\,$ [mm/d]'
            ylabel4 = '$ET\,$ [mm/d]'
        else:
            ylabel2 = '$Potential Evapotranspiration\,$ [in/d]'
            ylabel4 = '$ET\,$ [in/d]'
        
    ##########################################################
    #   Prepare the figure "canvas"                          #
    ##########################################################

    if not data_type == 'temperature':                                                          #Translates the data into a color map plot.
        cmap1 = mpl.colors.LinearSegmentedColormap.from_list('my_cmap',['white','blue'],256)
    else:
        cmap1 = mpl.colors.LinearSegmentedColormap.from_list('my_cmap',['white',(0.9,0.1,0.1)],256)
        
    fig = plt.figure(1, figsize=(12,8))
    width_ratios=[3.5, 1., 1.]
    height_ratios = [4., 1.5]
    wspace = 0.05     # horizontal space between figures
    hspace = 0.08     # vertical space between figures
    
    ###### Figure canvas left side
    if plot_structure == '3 by 2':
        gs1 = gridspec.GridSpec(2, 3, width_ratios=width_ratios,
                                height_ratios=height_ratios)
    elif plot_structure == '2 by 2':
        gs1 = gridspec.GridSpec(2, 2, width_ratios=width_ratios,
                                height_ratios=height_ratios)
        
    gs1.update(left=0.1, right = 1., wspace=wspace, hspace = hspace)
    
    ##########################################################
    #   Prep the first plot (cascade)                        #
    ##########################################################

    ax = fig.add_subplot(gs1[0,0])
    p = plt.imshow(data_2D_clipped, origin='lower', cmap = cmap1, aspect='auto',                     # with revised color ramp
                  extent=[cst.day_of_year_oct1, 365 + cst.day_of_year_oct1 - 1 , 2011, 2100]) 
    month_labels(ax)
    ax.set_ylabel('$Water \, Year$', fontsize=14)
    ticks=np.arange(2020,2100,10)
    plt.yticks(ticks, fontsize=14)
    plt.title(title+' 2010 - 2100', fontsize = 18)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.85, lw=0)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.04, aspect=20)
    plt.colorbar(p,cax=cax).set_label(ylabel2)

    ##########################################################
    #   Prep the fourth plot (bottom strip)                  #
    ##########################################################
    
    averaging_window = 59
    window_raw = np.array([])
    window_raw = np.append(window_raw,[n_take_k(averaging_window-1,i) for i in range(averaging_window)])
    window = window_raw / np.sum(window_raw)  # normalized weights

    # Calculate moving averages (using binomial filter - in movingaverage).
    # Prepend and append half of averaging window to data window so that moving average at early
    #   and late time are correct.

    data_early = movingaverage([np.mean(data_2D[0:29,i]) for i in range(365-averaging_window/2 , 364)] +
                               [np.mean(data_2D[0:29,i]) for i in range(365)] +
                               [np.mean(data_2D[0:29,i]) for i in range(0 , averaging_window/2)],
                               window)[averaging_window/2 : 365+averaging_window/2]
    data_mid   = movingaverage([np.mean(data_2D[30:59,i]) for i in range(365-averaging_window/2 , 364)] +
                               [np.mean(data_2D[30:59,i]) for i in range(365)] +
                               [np.mean(data_2D[30:59,i]) for i in range(0 , averaging_window/2)],
                               window)[averaging_window/2 : 365+averaging_window/2]
    data_late  = movingaverage([np.mean(data_2D[60:89,i]) for i in range(365-averaging_window/2 , 364)] +
                               [np.mean(data_2D[60:89,i]) for i in range(365)] +
                               [np.mean(data_2D[60:89,i]) for i in range(0 , averaging_window/2)],
                               window)[averaging_window/2 : 365+averaging_window/2]
    
    ax4 = fig.add_subplot(gs1[1,0], aspect = 'auto', sharex=ax)
    ax4.plot(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             data_early, color="0.62", lw=1.5)
    ax4.plot(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             data_mid, color="0.32", lw=1.5)
    ax4.plot(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             data_late, color="0.", lw=1.5)
##    if stats_available:
##        ax4.plot(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
##             movingaverage(mean_Q,window), 'k--', lw=1.5)
    month_labels(ax4)
    ax4.set_xlabel('$Month \, of \, Year$', fontsize=14)
    ax4.set_ylabel(ylabel4, fontsize=14)
##    if stats_available:
##        ax4.legend(('Early century', 'Mid century', 'Late century','20$^{\t{th}}$ century'),
##               'upper right',frameon=False, fontsize=12)
##    else:
    if not data_type == 'irrigation' and \
       not data_type == 'municipal' and \
       not data_type == 'water_rights' and \
       not data_type == 'temperature' and \
       not data_type == 'et' and \
       not data_type == 'potet':
        ax4.legend(('Early century', 'Mid century', 'Late century'),
                   'upper right',frameon=False, fontsize=12)
    else:
        ax4.legend(('Early century', 'Mid century', 'Late century'),
                   'upper left',frameon=False, fontsize=12)
            
        
    divider2 = make_axes_locatable(ax4)
    cax2 = divider2.append_axes("right", size="5%", pad=0.01)
    cax2.axis('off')
    cax2.set_visible(False)
    max_yticks = 5
    yloc = plt.MaxNLocator(max_yticks)
    ax4.yaxis.set_major_locator(yloc)
    plt.colorbar(cax=cax2)
    
    ##########################################################
    #   Prep the right side figure canvas                    #
    #   Generate parameters common to one or both plots      #
    ##########################################################
    
    if plot_structure == '3 by 2':
        gs2 = gridspec.GridSpec(2, 3, width_ratios=width_ratios,
                                height_ratios=height_ratios)
    elif plot_structure == '2 by 2':
        gs2 = gridspec.GridSpec(2, 2, width_ratios=width_ratios,
                                height_ratios=height_ratios)
        
    gs2.update(left=0.35, right = 0.94, wspace=wspace, hspace = hspace)
    
    max_xticks = 2
    y = range(2011,2100)
    dot_size = 40
    
    ##########################################################
    #   Prep the second plot (strip chart, right)            #
    ##########################################################
 
    ax2 = fig.add_subplot(gs2[0,1], aspect = 'auto', sharey=ax)
#   ax2.scatter(data_set_rhs_1, y, marker='o', s=dot_size, lw = 0)  # use this for scatterplot instead of box-and-whisker
    BoxPlot(ax2, data_set_rhs_1)
    xloc = plt.MaxNLocator(max_xticks)
    ax2.xaxis.set_major_locator(xloc)
    plt.yticks(ticks, fontsize=14)
    plt.ylim(2011,2100)
    if data_type == 'stream' or \
       data_type == 'daminWdup' or \
       data_type == 'damoutWdup' or \
       data_type == 'damin' or \
       data_type == 'damout':

        plt.xlabel('$Min \, Q$', fontsize = 14)
        
    elif data_type == 'snow':

        if SI:
            plt.xlabel('$Apr \, 1\, SWE$ [mm]', fontsize = 14)
        else:
            plt.xlabel('$Apr \, 1\, SWE$ [in]', fontsize = 14)
        
    elif data_type == 'precipitation':
        if SI:
            plt.xlabel('$Annual \, Precip$ [mm]', fontsize = 14)
        else:
            plt.xlabel('$Annual \, Precip$ [in]', fontsize = 14)
    
    elif data_type == 'irrigation':
        if SI:
            plt.xlabel('$Tot \, Ann \, Irrig\,$\n[million m$^3$]', fontsize = 14)
        else:
            plt.xlabel('$Tot \, Ann \, Irrig\,$\n[thousand ac-ft]', fontsize = 14)

    elif data_type == 'municipal':
        if SI:
            plt.xlabel('$Tot \, Ann \, Mncpl\,$\n[million m$^3$]', fontsize = 14)
        else:
            plt.xlabel('$Tot \, Ann \, Mncpl\,$\n[thousand ac-ft]', fontsize = 14)

    elif data_type == 'water_rights':
        if SI:
            plt.xlabel('$Tot \, Unxczd \, Wtr\, Rt\,$\n[million m$^3$]', fontsize = 14)
        else:
            plt.xlabel('$Tot \, Unxczd \, Wtr\, Rt\,$\n[thousand ac-ft]', fontsize = 14)

    elif data_type == 'temperature':
        if SI:
            plt.xlabel('$Min\,T\,$ [$^{\circ}\mathrm{C}$]', fontsize = 14)
        else:
            plt.xlabel('$Min\,T\,$ [$^{\circ}\mathrm{F}$]', fontsize = 14)
            

    elif data_type == 'et':
        if SI:
            plt.xlabel('$Tot \, ET$ [mm]', fontsize = 14)
        else:
            plt.xlabel('$Tot \, ET$ [in]', fontsize = 14)

    elif data_type == 'potet':
        if SI:
            plt.xlabel('$Tot \, PET$ [mm]', fontsize = 14)
        else:
            plt.xlabel('$Tot \, PET$ [in]', fontsize = 14)
            

    if plot_structure == '3 by 2':
        ax2.yaxis.set_visible(False)
                  
    elif plot_structure == '2 by 2':
        ax2.yaxis.tick_right()

    ##########################################################
    #   Prep the third plot (2nd strip chart, far right)     #
    ##########################################################

    if plot_structure == '3 by 2':
        ax3 = fig.add_subplot(gs2[0,2], aspect = 'auto', sharey=ax)
        if flood_Q_available:
            if not SI: flood_Q = flood_Q / cst.cfs_to_m3
            flood_Q_line = np.ones_like(np.append(Q_max,1)) * flood_Q
            plt.plot(flood_Q_line, np.append(np.array(y),2100), 'r-', lw=1.)
            textstr2 = 'Flood stage'
            props2 = dict(boxstyle='round', facecolor='w', alpha=0.5, lw=0)
            ax3.text(0.45, 0.31, textstr2, color='r', transform=ax3.transAxes,
                     fontsize=12, verticalalignment='top', bbox=props2, rotation = 'vertical')
            
#       ax3.scatter(Q_max, y, marker='o', s=dot_size, lw = 0)  # use this for scatterplot instead of box-and-whisker
        BoxPlot(ax3, data_set_rhs_2)
        xloc = plt.MaxNLocator(max_xticks)
        ax3.xaxis.set_major_locator(xloc)
        plt.ylim(2011,2100)
        ax3.yaxis.tick_right()
        plt.yticks(ticks, fontsize=14)
        if data_type == 'stream' or \
           data_type == 'daminWdup' or \
           data_type == 'damoutWdup' or \
           data_type == 'damin' or \
           data_type == 'damout':

            if SI:
                plt.xlabel('$Max \, Q$ [m$^{\t{3}}$/s]', fontsize = 14)
            else:
                plt.xlabel('$Max \, Q$ [cfs]', fontsize = 14)
            
        elif data_type == 'temperature':
            if SI:
                plt.xlabel('$Max \, T$ [$^{\circ}\mathrm{C}$]', fontsize = 14)
            else:
                plt.xlabel('$Max \, T$ [$^{\circ}\mathrm{F}$]', fontsize = 14)

    ###################################################################
    #   Add metadata text box in lower right, citing figure details   #
    ###################################################################
    import os.path,time
    textstr = 'Willamette Water 2100\n'+'Comparative case\n'+cst.metadata.model_run + ' Climate\n'+file_model_csv+'\n\nGenerated on '+str(datetime.date.today()) +'\nReference data retrieved on ' + time.ctime(os.path.getctime(file_1_w_path)) + '\nComparative data retrieved on ' + time.ctime(os.path.getctime(file_2_w_path))

    props = dict(boxstyle='round', facecolor='white', alpha=0.5, lw=0.)

    ax4.text(1.03, -0.2, textstr, transform=ax.transAxes, fontsize=6,
            verticalalignment='top', bbox=props)

    ##########################################################
    #   Save or display the plots                            #
    ##########################################################

    if Display:
        plt.show()
    else:
        file_graphics = graph_name + '.png'
        plt.savefig(file_graphics, format="png", dpi=300)
    plt.close(1)
    

#   End of script for cascade plots

########################################################################################
########################################################################################
########################################################################################
    
#  Supporting functions

def n_take_k(n,k):
    """Returns (n take k),
    the binomial coefficient.

    author: https://code.google.com/p/econpy/source/browse/trunk/pytrix/pytrix.py
    """
    n, k = int(n), int(k)
    assert (0<=k<=n), "n=%f, k=%f"%(n,k)
    k = min(k,n-k)
    c = 1
    if k>0:
        for i in xrange(k):
            c *= n-i
            c //= i+1
    return c

def movingaverage(interval, window):
    """
    Calculate a moving average and return numpy array (dimension 1)
    """
    import numpy as np
#    window = np.ones(int(window_size))/float(window_size
    return np.convolve(interval, window, 'same')

def movingaverage_first2D(array_2D, window_size_days, window_size_yrs):
    """
    Calculate a moving average of first window_size_yrs years over
      a window of window_size_days, and return a numpy array (dimension 1)
    """
    import numpy as np
    interval = [np.average(array_2D[0:window_size_yrs,i]) for i in range(365)]
    window = np.ones(int(window_size_days))/float(window_size_days)
    return np.convolve(interval, window, 'same')

def month_labels (axys):
    """
    Place month labels on horizontal axis.  This is a little tricky,
       so I found some code on the web and modified it.
    """
    from pylab import plot, ylim, xlim, show, xlabel, ylabel, grid
    import matplotlib.pyplot as plt
    import matplotlib.dates as dates
    import datetime
    import matplotlib.ticker as ticker

    axys.xaxis.set_major_locator(dates.MonthLocator())
    axys.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=15))
    axys.xaxis.set_major_formatter(ticker.NullFormatter())
    axys.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
    for tick in axys.xaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')
    return

def BoxPlot(axys, variable):
    """
    Create and plot the boxes for the box-and-whisker plot
    """
    import matplotlib.pyplot as plt
    import numpy as np
    variableT = variable.T
    col = (0.6,0.6,1.)  # light blue in rgb
    positions=range(2015,2096,10)
    box = axys.boxplot(variableT, vert=False,positions=positions,widths=9.2,
                       whis=2,sym='',patch_artist=True)
    plt.setp(box['boxes'], color=col)
    colors = [col]*9
    for patch, colors in zip(box['boxes'], colors):
        patch.set_facecolor(colors)
    for cap in box['caps']:
        cap.set(linewidth = 0)
    for whisker in box['whiskers']:
        whisker.set_linestyle('solid')
        whisker.set_linewidth(1)
    return


########################################################################################
########################################################################################
########################################################################################

######################################################
#####   SCRIPT TO GENERATE THE PLOTS             #####
######################################################
"""
 This script generates a set of plots by first reading in the names of files
 and associated parameters from an xls file.  That file is called
 "cascade plot parameters.xls"
"""
# kwargs:
#   data_type = 'stream' (default), daminWdup, damin,
#               damoutWdup, damout                    damWdup means file has duplicate data
#   flood_Q_available = False (default), True
#   Display = False (default), True
#   stats_available = False (default), True
#   SI = True (default), False

def run():
    import comparative_constants as cst   # constants.py contains constants used here
    import xlrd

    # Read a parameter file in xls format.
    cascade_plot_params = xlrd.open_workbook('Master File.xls')

    reference_file = cascade_plot_params.sheet_by_index(0).col_values(0)[1:]
    compared_file = cascade_plot_params.sheet_by_index(0).col_values(1)[1:]
    title = cascade_plot_params.sheet_by_index(0).col_values(2)[1:]                 # title for plot
    ToBePlotted = cascade_plot_params.sheet_by_index(0).col_values(3)[1:]           # make this plot? True or False
    Display_v = cascade_plot_params.sheet_by_index(0).col_values(4)[1:]             # Display plot on screen (True) or as png file (False)
    flood_Q = cascade_plot_params.sheet_by_index(0).col_values(5)[1:]               # Flood discharge in cfs, if known
    flood_Q_available_v = cascade_plot_params.sheet_by_index(0).col_values(6)[1:]   # We know flood discharge (True/False)
    data_type_v = cascade_plot_params.sheet_by_index(0).col_values(7)[1:]           # What type of data is this? Stream, Dam, etc.
    SI_v = cascade_plot_params.sheet_by_index(0).col_values(8)[1:]                  # Metric or standard units

##    print type(flood_Q[0])
##    print type(cst.cfs_to_m3)
##    print flood_Q[30]*cst.cfs_to_m3
    flood_Q[:] = [element*cst.cfs_to_m3 for element in flood_Q[:]]   # convert flood_Q from cfs to m3/s
    total_number_of_plots = len(reference_file)


    # Make the plots.
    for plot_number in range(total_number_of_plots):
        if ToBePlotted[plot_number]:
            compare(
                reference_file[plot_number],
                compared_file[plot_number],
                title[plot_number],
                flood_Q[plot_number],
                Display = Display_v[plot_number],
    ##            Display = True,
                data_type = data_type_v[plot_number],
                flood_Q_available = flood_Q_available_v[plot_number],
                SI = SI_v[plot_number]
                )
    return

run()
