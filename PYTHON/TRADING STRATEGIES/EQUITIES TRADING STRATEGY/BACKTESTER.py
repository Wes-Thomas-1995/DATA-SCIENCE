

import pandas as pd
from math import floor
import datetime as dt 
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt






def BACKTEST(data, testing, investment_amount, BACKTEST_CHOSEN, BACKTEST_RUN):
    
    def simple_cumulative(testing, strategy, investment_amount):
        investment_origin               = investment_amount
        df_date                         = testing
        
        df_date.reset_index(inplace = True)
        
        df_date                         = df_date.rename(columns={"Date":"date"})
        end_val                         = len(df_date)-1
        start_1                         = df_date.at[0,'date']
        end_1                           = df_date.at[end_val,'date']
        
        if isinstance(df_date.at[0,'date'], pd.Timestamp) == True:
            pass
        else:
            start_1             = datetime.strptime(start_1, "%Y/%m/%d")
            end_1               = datetime.strptime(end_1, "%Y/%m/%d")
        
        
        delta                   = (end_1 - start_1).days        
        testing['return']       = testing['diff'] * testing['signal']
        testing['expense']      = testing['return'] * 0.98
        j                       = 1
        grouping                = [0]
        pricing                 = [0]
        quant                   = []
        invest                  = []
        grown                   = []
        
        for i in range(1,len(testing)-1):
            if i == 1 and testing.at[i, 'signal'] == 1:
                grouping.append(j)
                pricing.append(testing.iat[i, 1])
                
                if testing.at[i + 1, 'signal'] == 0:
                    j = j + 1
                
            elif testing.at[i, 'signal'] == 1 and testing.at[i + 1, 'signal'] == 0 and testing.at[i - 1, 'signal'] == 0:
                grouping.append(j)
                pricing.append(testing.iat[i, 1])
                j = j + 1
            elif testing.at[i, 'signal'] == 1 and testing.at[i + 1, 'signal'] == 0:
                grouping.append(j)
                pricing.append(0)
                j = j + 1
            elif testing.at[i, 'signal'] == 1 and testing.at[i - 1, 'signal'] == 0:
                grouping.append(j)
                pricing.append(testing.iat[i, 1])
            elif testing.at[i, 'signal'] == 1:
                grouping.append(j)
                pricing.append(0)
            else:
                grouping.append(0)
                pricing.append(0)

        if testing.at[len(testing)-1, 'signal'] == 1 and testing.at[len(testing)-2, 'signal'] == 1:
            grouping.append(j)
            pricing.append(0)
        elif testing.at[len(testing)-1, 'signal'] == 1 and testing.at[len(testing)-2, 'signal'] == 0:
            grouping.append(j)
            pricing.append(testing.iat[len(testing)-1, 1])
        else:
            grouping.append(0)
            pricing.append(0)
        
        testing['grouping']                 = grouping
        testing['price']                    = pricing
        df2                                 = testing.groupby('grouping').agg({'expense':sum, 'price':sum, 'grouping':'count'}).rename(columns={'grouping':'count', 'expense':'total_return', 'price':'pricing'})  
        df2                                 = df2[df2.index != 0]    
        max_duration                        = df2['count'].max()
        days_holding                        = df2['count'].sum()
        nbr_trades                          = len(df2)
        avr_holding                         = days_holding / nbr_trades

        
        for i in range(1,len(df2)+1):
            invest.append(investment_amount)
            round(investment_amount/df2.at[i,'pricing'], 4)
            quantity                        = round(investment_amount/df2.at[i,'pricing'], 4)
            growth                          = ((df2.at[i, 'total_return'] * quantity) / investment_amount) * 100
            investment_amount               = (df2.at[i, 'total_return'] * quantity) + investment_amount
            quant.append(quantity)
            grown.append(growth)
            
        df2['investment_amount']            = invest
        df2['quantity']                     = quant
        df2['growth']                       = grown
        df2.reset_index(inplace=True)
        max_return_1                        = df2['growth'].max()
        min_return_1                        = df2['growth'].min()
        pos_count                           = 0
        val                                 = len(grown)
        
        for num in grown:
            if num >= 0:
                pos_count += 1

        if pos_count == 0 or val == 0:
            win_rate                            = 0
        else:
            win_rate                            = round((pos_count/val)*100,1)
        
        testing                             = testing.merge(df2,how='left', left_on='grouping', right_on='grouping')
        testing                             = testing.fillna(0)
        testing['price']                    = testing['pricing']
        testing['year']                     = pd.DatetimeIndex(testing['Date']).year
        testing['true_return']              = testing['expense'] * testing['quantity']
        portfolio_value                     = [investment_origin]

        for i in range(1,len(testing)):
            portfolio_value_app = investment_origin + testing.loc[0:i, 'true_return'].sum()
            portfolio_value.append(portfolio_value_app)
            
        testing['portfolio_value']                  = portfolio_value
        testing['portfolio_growth']                 = round(((testing['portfolio_value']/investment_origin)-1)*100,1)
        testing['maximum_value']                    = testing['portfolio_value'].max()
        cols                                        = ['Date', 'open', 'high', 'low', 'close', 'diff', 'signal', 'year', 'return', 'expense', 'grouping', 
                                                        'price', 'investment_amount', 'quantity', 'true_return', 'portfolio_value', 'portfolio_growth', 'maximum_value','count','total_return', 'pricing']
        
        testing                                     = testing[cols]
        testing                                     = testing.drop(['total_return', 'pricing'], axis=1)
        total_growth_value                          = testing['true_return'].sum()
        total_return                                = total_growth_value + investment_origin
        total_growth_per                            = ((total_return / investment_origin)-1) * 100
        start_2                                     = start_1.strftime("%Y-%m-%d") 
        end_2                                       = end_1.strftime("%Y-%m-%d") 
        MIN_YEAR                                    = testing['year'].min()
        cy                                          = int(dt.date.today().strftime("%Y")) 
        ly                                          = int((datetime.now() - relativedelta(years=1)).strftime("%Y"))
        ty                                          = int((datetime.now() - relativedelta(years=2)).strftime("%Y"))
        CY_MIN_VAL, PY_MIN_VAL, TWOY_MIN_VAL        = "", "", ""
        YTD_RETURN, PREV_Y_RETURN, TWO_Y_RETURN     = 0, 0, 0
        CY_growth, PY_growth, TY_growth             = 0, 0, 0

        if MIN_YEAR == cy:
            current_year                            = int(dt.date.today().strftime("%Y"))  
            CY_MIN_VAL                              = testing.loc[(testing['year'] == current_year), 'portfolio_value'].reset_index(drop=True)
            CY_MIN_VAl_1                            = CY_MIN_VAL.iloc[0,]
            YTD_RETURN                              = total_return - CY_MIN_VAl_1
            CY_growth                               = (YTD_RETURN / CY_MIN_VAl_1)*100
            
        if MIN_YEAR == ly:
            current_year                            = int(dt.date.today().strftime("%Y")) 
            last_year                               = int((datetime.now() - relativedelta(years=1)).strftime("%Y"))
            CY_MIN_VAL                              = testing.loc[(testing['year'] == current_year), 'portfolio_value'].reset_index(drop=True)
            PY_MIN_VAL                              = testing.loc[(testing['year'] == last_year), 'portfolio_value'].reset_index(drop=True)
            
            CY_MIN_VAl_1                            = CY_MIN_VAL.iloc[0,]
            PY_MIN_VAl_1                            = PY_MIN_VAL.loc[0,]
            
            YTD_RETURN                              = total_return - CY_MIN_VAl_1
            PREV_Y_RETURN                           = CY_MIN_VAl_1 - PY_MIN_VAl_1
            CY_growth                               = (YTD_RETURN / CY_MIN_VAl_1)*100
            PY_growth                               = (PREV_Y_RETURN / PY_MIN_VAl_1)*100
            
        if MIN_YEAR <= ty:
            current_year                    = int(dt.date.today().strftime("%Y")) 
            last_year                       = int((datetime.now() - relativedelta(years=1)).strftime("%Y")) 
            two_year                        = int((datetime.now() - relativedelta(years=2)).strftime("%Y"))           
            CY_MIN_VAL                      = testing.loc[(testing['year'] == current_year), 'portfolio_value'].reset_index(drop=True)
            PY_MIN_VAL                      = testing.loc[(testing['year'] == last_year), 'portfolio_value'].reset_index(drop=True)
            TWOY_MIN_VAL                    = testing.loc[(testing['year'] == two_year), 'portfolio_value'].reset_index(drop=True)
            
            CY_MIN_VAl_1                    = CY_MIN_VAL.iloc[0,]
            PY_MIN_VAl_1                    = PY_MIN_VAL.iloc[0,]
            TWOY_MIN_VAl_1                  = TWOY_MIN_VAL.iloc[0,]
            
            YTD_RETURN                      = total_return - CY_MIN_VAl_1
            PREV_Y_RETURN                   = CY_MIN_VAl_1 - PY_MIN_VAl_1
            TWO_Y_RETURN                    = PY_MIN_VAl_1 - TWOY_MIN_VAl_1
            CY_growth                       = (YTD_RETURN / CY_MIN_VAl_1)*100
            PY_growth                       = (PREV_Y_RETURN / PY_MIN_VAl_1)*100
            TY_growth                       = (TWO_Y_RETURN / TWOY_MIN_VAl_1)*100       
        
        exposure_time                       = round(((days_holding/delta)*100),1)
        average_return                      = total_growth_per/nbr_trades
        

        
        full_details = [start_2, end_2, delta, exposure_time, investment_origin, total_return, total_growth_per,
                        YTD_RETURN, PREV_Y_RETURN, TWO_Y_RETURN, CY_growth, PY_growth, TY_growth, nbr_trades,
                        win_rate, max_return_1, min_return_1, average_return, max_duration, avr_holding]
        
        
        return testing, full_details

    
    def simple_non_cumulative(testing, strategy, investment_amount):
        investment_origin               = investment_amount
        df_date                         = testing
        
        df_date.reset_index(inplace = True)
        
        df_date                         = df_date.rename(columns={"Date":"date"})
        end_val                         = len(df_date)-1
        start_1                         = df_date.at[0,'date']
        end_1                           = df_date.at[end_val,'date']
        
        if isinstance(df_date.at[0,'date'], pd.Timestamp) == True:
            pass
        else:
            start_1             = datetime.strptime(start_1, "%Y/%m/%d")
            end_1               = datetime.strptime(end_1, "%Y/%m/%d")
        
        
        delta                   = (end_1 - start_1).days
        
        testing['return']       = testing['diff'] * testing['signal']
        testing['expense']      = testing['return'] * 0.98
        j                       = 1
        grouping                = [0]
        pricing                 = [0]
        quant                   = []
        invest                  = []
        grown                   = []
        
        for i in range(1,len(testing)-1):
            if i == 1 and testing.at[i, 'signal'] == 1:
                grouping.append(j)
                pricing.append(testing.iat[i, 1])
                
                if testing.at[i + 1, 'signal'] == 0:
                    j = j + 1
                
            elif testing.at[i, 'signal'] == 1 and testing.at[i + 1, 'signal'] == 0 and testing.at[i - 1, 'signal'] == 0:
                grouping.append(j)
                pricing.append(testing.iat[i, 1])
                j = j + 1
            elif testing.at[i, 'signal'] == 1 and testing.at[i + 1, 'signal'] == 0:
                grouping.append(j)
                pricing.append(0)
                j = j + 1
            elif testing.at[i, 'signal'] == 1 and testing.at[i - 1, 'signal'] == 0:
                grouping.append(j)
                pricing.append(testing.iat[i, 1])
            elif testing.at[i, 'signal'] == 1:
                grouping.append(j)
                pricing.append(0)
            else:
                grouping.append(0)
                pricing.append(0)

        if testing.at[len(testing)-1, 'signal'] == 1 and testing.at[len(testing)-2, 'signal'] == 1:
            grouping.append(j)
            pricing.append(0)
        elif testing.at[len(testing)-1, 'signal'] == 1 and testing.at[len(testing)-2, 'signal'] == 0:
            grouping.append(j)
            pricing.append(testing.iat[len(testing)-1, 1])
        else:
            grouping.append(0)
            pricing.append(0)

        testing['grouping']                 = grouping
        testing['price']                    = pricing
        df2                                 = testing.groupby('grouping').agg({'expense':sum, 'price':sum, 'grouping':'count'}).rename(columns={'grouping':'count', 'expense':'total_return', 'price':'pricing'})  
        df2                                 = df2[df2.index != 0]    
        max_duration                        = df2['count'].max()
        days_holding                        = df2['count'].sum()
        nbr_trades                          = len(df2)
        avr_holding                         = days_holding / nbr_trades

        
        for i in range(1,len(df2)+1):
            invest.append(investment_amount)
            quantity                        = round(investment_amount/df2.at[i,'pricing'], 4)
            growth                          = ((df2.at[i, 'total_return'] * quantity) / investment_amount) * 100
            quant.append(quantity)
            grown.append(growth)
            
        df2['investment_amount']            = invest
        df2['quantity']                     = quant
        df2['growth']                       = grown
        df2.reset_index(inplace=True)
        max_return_1                        = df2['growth'].max()
        min_return_1                        = df2['growth'].min()
        pos_count                           = 0
        val                                 = len(grown)
        
        for num in grown:
            if num >= 0:
                pos_count += 1

        if pos_count == 0 or val == 0:
            win_rate                            = 0
        else:
            win_rate                            = round((pos_count/val)*100,1)
        
        testing                             = testing.merge(df2,how='left', left_on='grouping', right_on='grouping')
        testing                             = testing.fillna(0)
        testing['price']                    = testing['pricing']
        testing['year']                     = pd.DatetimeIndex(testing['Date']).year
        testing['true_return']              = testing['expense'] * testing['quantity']
        portfolio_value                     = [investment_origin]

        for i in range(1,len(testing)):
            portfolio_value_app = investment_origin + testing.loc[0:i, 'true_return'].sum()
            portfolio_value.append(portfolio_value_app)
            
        testing['portfolio_value']                  = portfolio_value
        testing['portfolio_growth']                 = round(((testing['portfolio_value']/investment_origin)-1)*100,1)
        testing['maximum_value']                    = testing['portfolio_value'].max()
        cols                                        = ['Date', 'open', 'high', 'low', 'close', 'diff', 'signal', 'year', 'return', 'expense', 'grouping', 
                                                        'price', 'investment_amount', 'quantity', 'true_return', 'portfolio_value', 'portfolio_growth', 'maximum_value','count','total_return', 'pricing']
        
        testing                                     = testing[cols]
        testing                                     = testing.drop(['total_return', 'pricing'], axis=1)
        total_growth_value                          = testing['true_return'].sum()
        total_return                                = total_growth_value + investment_origin
        total_growth_per                            = ((total_return / investment_origin)-1) * 100
        start_2                                     = start_1.strftime("%Y-%m-%d") 
        end_2                                       = end_1.strftime("%Y-%m-%d") 
        MIN_YEAR                                    = testing['year'].min()
        cy                                          = int(dt.date.today().strftime("%Y")) 
        ly                                          = int((datetime.now() - relativedelta(years=1)).strftime("%Y"))
        ty                                          = int((datetime.now() - relativedelta(years=2)).strftime("%Y"))
        CY_MIN_VAL, PY_MIN_VAL, TWOY_MIN_VAL        = "", "", ""
        YTD_RETURN, PREV_Y_RETURN, TWO_Y_RETURN     = 0, 0, 0
        CY_growth, PY_growth, TY_growth             = 0, 0, 0

        if MIN_YEAR == cy:
            current_year                            = int(dt.date.today().strftime("%Y"))  
            CY_MIN_VAL                              = testing.loc[(testing['year'] == current_year), 'portfolio_value'].reset_index(drop=True)
            CY_MIN_VAl_1                            = CY_MIN_VAL.iloc[0,]
            YTD_RETURN                              = total_return - CY_MIN_VAl_1
            CY_growth                               = (YTD_RETURN / CY_MIN_VAl_1)*100
            
        if MIN_YEAR == ly:
            current_year                            = int(dt.date.today().strftime("%Y")) 
            last_year                               = int((datetime.now() - relativedelta(years=1)).strftime("%Y"))
            CY_MIN_VAL                              = testing.loc[(testing['year'] == current_year), 'portfolio_value'].reset_index(drop=True)
            PY_MIN_VAL                              = testing.loc[(testing['year'] == last_year), 'portfolio_value'].reset_index(drop=True)
            
            CY_MIN_VAl_1                            = CY_MIN_VAL.iloc[0,]
            PY_MIN_VAl_1                            = PY_MIN_VAL.loc[0,]
            
            YTD_RETURN                              = total_return - CY_MIN_VAl_1
            PREV_Y_RETURN                           = CY_MIN_VAl_1 - PY_MIN_VAl_1
            CY_growth                               = (YTD_RETURN / CY_MIN_VAl_1)*100
            PY_growth                               = (PREV_Y_RETURN / PY_MIN_VAl_1)*100
            
        if MIN_YEAR <= ty:
            current_year                    = int(dt.date.today().strftime("%Y")) 
            last_year                       = int((datetime.now() - relativedelta(years=1)).strftime("%Y")) 
            two_year                        = int((datetime.now() - relativedelta(years=2)).strftime("%Y"))           
            CY_MIN_VAL                      = testing.loc[(testing['year'] == current_year), 'portfolio_value'].reset_index(drop=True)
            PY_MIN_VAL                      = testing.loc[(testing['year'] == last_year), 'portfolio_value'].reset_index(drop=True)
            TWOY_MIN_VAL                    = testing.loc[(testing['year'] == two_year), 'portfolio_value'].reset_index(drop=True)
            
            CY_MIN_VAl_1                    = CY_MIN_VAL.iloc[0,]
            PY_MIN_VAl_1                    = PY_MIN_VAL.iloc[0,]
            TWOY_MIN_VAl_1                  = TWOY_MIN_VAL.iloc[0,]
            
            YTD_RETURN                      = total_return - CY_MIN_VAl_1
            PREV_Y_RETURN                   = CY_MIN_VAl_1 - PY_MIN_VAl_1
            TWO_Y_RETURN                    = PY_MIN_VAl_1 - TWOY_MIN_VAl_1
            CY_growth                       = (YTD_RETURN / CY_MIN_VAl_1)*100
            PY_growth                       = (PREV_Y_RETURN / PY_MIN_VAl_1)*100
            TY_growth                       = (TWO_Y_RETURN / TWOY_MIN_VAl_1)*100       
        

        exposure_time = round(((days_holding/delta)*100),1)
        average_return = total_growth_per/nbr_trades
        
        full_details = [start_2, end_2, delta, exposure_time, investment_origin, total_return, total_growth_per,
                        YTD_RETURN, PREV_Y_RETURN, TWO_Y_RETURN, CY_growth, PY_growth, TY_growth, nbr_trades,
                        win_rate, max_return_1, min_return_1, average_return, max_duration, avr_holding]
        
        
        return testing, full_details
    
    
    def multiple_cumulative(data, signals, strategy, investment_amount):
        LENGTH = len(data)
        testing = []
        
        performance_df = pd.DataFrame(columns=['ticker', 'start_date', 'end_date', 'delta', 'exposure_time',
                                                'investment_origin', 'total_return', 'total_growth_per', 'YTD_RETURN', 'PREV_Y_RETURN',
                                                'TWO_Y_RETURN', 'CY_growth', 'PY_growth', 'TY_growth', 'nbr_trades', 'win_rate', 'max_return_1',
                                                'min_return_1', 'average_return', 'max_duration', 'avr_holding'])
        
        for i in range(LENGTH):
            test                    = signals[i]
            test, full_details      = simple_cumulative(test, strategy, investment_amount)
            
            root = (r'/Users/westhomas/Desktop')
            #test.to_csv(root + '/' + data[i] + ' Backtest output of strategy output.csv')
            
            performance_df          = performance_df.append({'ticker'                : data[i],
                                                            'start_date'            : full_details[0],
                                                            'end_date'              : full_details[1],
                                                            'delta'                 : full_details[2],
                                                            'exposure_time'         : full_details[3],
                                                            'investment_origin'     : full_details[4],
                                                            'total_return'          : full_details[5],
                                                            'total_growth_per'      : full_details[6],
                                                            'YTD_RETURN'            : full_details[7],
                                                            'PREV_Y_RETURN'         : full_details[8],
                                                            'TWO_Y_RETURN'          : full_details[9],
                                                            'CY_growth'             : full_details[10],
                                                            'PY_growth'             : full_details[11],
                                                            'TY_growth'             : full_details[12],
                                                            'nbr_trades'            : full_details[13],
                                                            'win_rate'              : full_details[14],
                                                            'max_return_1'          : full_details[15],
                                                            'min_return_1'          : full_details[16],
                                                            'average_return'        : full_details[17],
                                                            'max_duration'          : full_details[18],
                                                            'avr_holding'           : full_details[19]}, ignore_index=True)
            
            testing.append(test)
            

            
        return testing, performance_df
        
        


    root = (r'/Users/westhomas/Desktop')

    if BACKTEST_RUN == 'YES':


        if isinstance(data, str) is True:
            if BACKTEST_CHOSEN == 'SNC':
                strategy = 'simple-non-cumulative'
            elif BACKTEST_CHOSEN == 'SC':
                strategy = 'simple-cumulative'
            
        else:
            strategy  = 'multiple-cumulative'
            

        if strategy == 'simple-cumulative':
            output, full_details = simple_cumulative(testing, strategy, investment_amount)
            strat = 'Simple Cumulative'
            performance_df = ""
            
        elif strategy == 'simple-non-cumulative':
            output, full_details = simple_non_cumulative(testing, strategy, investment_amount)
            strat = 'Simple Non -- Cumulative'
            performance_df = ""
            
        elif strategy == 'multiple-cumulative':
            output, performance_df = multiple_cumulative(data, testing, strategy, investment_amount)   
            #performance_df.to_csv(root + '/' + 'PERFORMANCE_OF_BACKTEST STRATEGY - 1Y - ' + strategy + '.csv')   


        if strategy == 'simple-cumulative' or strategy == 'simple-non-cumulative':
            
            start_2             = full_details[0]
            end_2               = full_details[1]
            delta               = full_details[2]
            exposure_time       = full_details[3]
            investment_origin   = full_details[4]
            total_return        = full_details[5]
            total_growth_per    = full_details[6]
            YTD_RETURN          = full_details[7]
            PREV_Y_RETURN       = full_details[8]
            TWO_Y_RETURN        = full_details[9] 
            CY_growth           = full_details[10]
            PY_growth           = full_details[11]
            TY_growth           = full_details[12]
            nbr_trades          = full_details[13]
            win_rate            = full_details[14]
            max_return_1        = full_details[15]
            min_return_1        = full_details[16]
            average_return      = full_details[17]
            max_duration        = full_details[18]
            avr_holding         = full_details[19]
            
            print("\n     - BACKTESTING STRATEGY :  " + strat)
            print("         - Ticker                             :  " + data)
            print("         - Start Date                         :  " + start_2)
            print("         - End Date                           :  " + end_2)
            print("         - Duration                           :  " + str(delta) + " days")
            print("         - Exposure Time                 [%]  :  " + str(exposure_time))
            print(" ")
                
            print("\n         Return Statistics     ")
            print("         - Original Investment Amount    [$]  :  {:,}".format(round(investment_origin),0))
            print("         - Total Return Amount           [$]  :  {:,}".format(round(total_return),0))
            print("         - Total Return Percentage       [%]  :  " + str(round(total_growth_per,1)))
            print(" ")
                
            print("\n         Annualised Statistics     ")
            print("         - Current Year Return (Ann.)    [$]  :  {:,}".format(round(YTD_RETURN),0))
            print("         - Previous Year Return (Ann.)   [$]  :  {:,}".format(round(PREV_Y_RETURN),0))
            print("         - Two Year Prior  Return (Ann.) [$]  :  {:,}".format(round(TWO_Y_RETURN),0))
            print("\n         - Current Year Return (Ann.)    [%]  :  " + str(round(CY_growth, 1)))
            print("         - Previous Year Return (Ann.)   [%]  :  " + str(round(PY_growth, 1)))
            print("         - Two Year Prior  Return (Ann.) [%]  :  " + str(round(TY_growth, 1)))
            print(" ")
                
            print("\n         Traded Statistics     ")
            print("         - Nbr of Trades                      :  " + str(nbr_trades))
            print("         - Win Rate                      [%]  :  " + str(win_rate)) 
            print("         - Best Trade                    [%]  :  " + str(round(max_return_1, 1)))     
            print("         - Worst Trade                   [%]  :  " + str(round(min_return_1, 1)))
            print("         - Avg. Trade                    [%]  :  " + str(round(average_return,1)))            
            print("         - Max. Trade Duration                :  " + str(round(max_duration,1)) + " days")
            print("         - Avg. Trade Duration                :  " + str(round(avr_holding,1)) + " days")
            print(" ")     
            
            if strategy == 'simple-cumulative':
                title_strat = "  Simple Cumulative Backtest Strategy  "
                
            else:
                title_strat = "  Simple Non -- Cumulative Backtest Strategy  "       
                
            fig, ax = plt.subplots()
            ax = plt.plot(output.Date, output.portfolio_value, 'g', label='Portfolio Value')
            ax = plt.plot(output.Date, output.maximum_value, 'r', label='Maximum Value', linestyle="--")
            ax = plt.title(title_strat)
            ax = plt.ticklabel_format(style='plain', axis='y')
            plt.legend()
            plt.show()   
             
        else:
            
            RETURN = performance_df["total_return"].mean()
            RETURN_TOTAL = RETURN - investment_amount
            RETURN_PER_TOTAL = (RETURN_TOTAL/investment_amount)*100

            MIN = performance_df["total_return"].min()
            MIN_TOTAL = MIN - investment_amount
            MIN_PER_TOTAL = (MIN_TOTAL/investment_amount)*100

            MAX = performance_df["total_return"].max()
            MAX_TOTAL = MAX - investment_amount
            MAX_PER_TOTAL = (MAX_TOTAL/investment_amount)*100           
            
            
            print("\n     - BACKTESTING STRATEGY :  Multiple Tickers - Simple Non -- Cumulative")
            print("         - Average Return Amount         [$]  :  {:,}".format(round(RETURN_TOTAL),0))
            print("         - Average Return Percentage     [%]  :  " + str(round(RETURN_PER_TOTAL,1)))

            print("\n         - Max Return Amount             [$]  :  {:,}".format(round(MAX_TOTAL),0))
            print("         - Max Return Percentage         [%]  :  " + str(round(MAX_PER_TOTAL,1)))
            
            print("\n         - Min Return Amount             [$]  :  {:,}".format(round(MIN_TOTAL),0))
            print("         - Min Return Percentage         [%]  :  " + str(round(MIN_PER_TOTAL,1)))



    elif BACKTEST_RUN == 'NO':
        output                      = ""
        performance_df              =""

  



    
    return output, performance_df





