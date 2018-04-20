

#%%
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd
import urllib
from tqdm import tqdm
from tqdm import trange
from time import sleep
import os

# ticker = 'ge'
# market = 'composite'
# nearby = -1

# money = 'all'

#%%

class NQOptions():

    def __init__(self, ticker, market = 'composite', nearby = -1, money = 'all'):
        self.ticker = ticker.lower()
        self.market = market
        self.nearby = nearby
        self.money = money

    def get_pg_nbs(self):
        url = 'http://www.nasdaq.com/symbol/{0}/option-chain?excode={1}&money={2}&date\
index={3}'.format(self.ticker, self.market, self.money, self.nearby)
        try:
            response = requests.get(url, timeout= 10)
#             DNS lookup failure
        except requests.exceptions.Timeout:
            self.money = 'near'
            url = 'http://www.nasdaq.com/symbol/{0}/option-chain?excode={1}&money={2}&date\
index={3}'.format(self.ticker, self.market, self.money, self.nearby)
            response = requests.get(url)

        except requests.exceptions.ConnectionError as e:
            print('''Webpage doesn't seem to exist!\n%s''' % e)
            pass
#             Timeout failure
        except requests.exceptions.ConnectTimeout as e:
            print('''Slow connection!\n%s''' % e)
            pass
#         HTTP error
        except requests.exceptions.HTTPError as e:
            print('''HTTP error!\n%s''' % e)
            pass


  ############################  ############################  ############################  ############################

        soup = BeautifulSoup(response.content, 'html.parser')
        last_page_raw = soup.find('a', {'id': 'quotes_content_left_lb_LastPage'})
        last_page = re.findall(pattern='(?:page=)(\d+)', string=str(last_page_raw))
        pg_nb = ''.join(last_page)
        if pg_nb != '':
            return int(pg_nb)
        elif pg_nb == '':
            return int(1.0)
        else:
            return("Sorry, couldn't find total pages to scrape from")



    def scraper(self):

        pg_nb = self.get_pg_nbs()
        old_df = pd.DataFrame()


        bar = trange(1, pg_nb+1, unit = 'link', leave = True)
        for i in bar:
            bar.set_description('Scraping link {0} of {1}'.format(i, pg_nb),
                                refresh = False)

            url = 'http://www.nasdaq.com/symbol/{0}/option-chain?excode={1}&money={2}&date\
index={3}&page={4}'.format(self.ticker, self.market, self.money, self.nearby, (i))


            try:
                response = requests.get(url)#, timeout=0.1)
            # DNS lookup failure
            except requests.exceptions.ConnectionError as e:
                print('''Webpage doesn't seem to exist!\n%s''' % e)
                pass
            # Timeout failure
            except requests.exceptions.ConnectTimeout as e:
                print('''Slow connection!\n%s''' % e)
                pass
            # HTTP error
            except requests.exceptions.HTTPError as e:
                print('''HTTP error!\n%s''' % e)
                pass



            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find_all('table')[5]
            rem = [i for i in table.find_all('td', {'colspan': '8'})]
            elems = table.find_all('td')
            lst = [elem.text for elem in elems if elem not in rem]
            arr = np.array(lst)

            reshaped = arr.reshape(int(len(lst)/16), int(16))

            old_df = pd.concat([old_df, pd.DataFrame(reshaped)])

            if old_df.shape[0]> 0:
                continue

            else:
                "The scraper didnt fetch any data"
        return old_df


    def get_options_data(self, save = False, folder = None, save_format = 'xlsx', ):
        """Function to make dataframe from the options data scraped from NASDAQ website
        Params:
            save: (boolean, optional) whether you want to save it or not,default is False
            folder: (str, optional)folder to save in, could be existing folder
            save_format: supported formats are 'xlsx'(default), 'xls', 'csv', 'txt'

        Returns a Dataframe
        """
        old_df = self.scraper()
        print('\n\nCreating DataFrames for {}'.format(self.ticker.upper()))
        sleep(3)
        old_df.replace('', np.nan, inplace= True)
        old_df = old_df.astype(int, errors = 'ignore')
        old_df.rename(columns = {8: 'Strike'}, inplace = True)
        date = pd.DatetimeIndex(old_df[0], name = 'Date')
        date = [i.date().strftime('%Y-%m-%d') for i in date]
        index = [date, old_df.Strike]
        calls = old_df.iloc[:, 1:7]
        puts = old_df.iloc[:, 10:16]
        calls.set_index(index, inplace= True)
        puts.set_index(index, inplace= True)
        headers = ['Last', 'Chg', 'Bid', 'Ask', 'Vol', 'OI']
        calls.columns = headers
        puts.columns = headers

        empty = pd.DataFrame(np.nan, index = calls.index, columns=[''])
        final_df = pd.concat([calls, empty, puts], keys = ['Call', ' ', 'Put'], axis = 1)
        if save:
            if folder:
                if type(folder) == str:
                    path = os.path.join(os.getcwd(), folder, self.ticker.upper())
                    if os.path.exists(path):
                        print('Saving data in {}'.format(str(path)))
                        sleep(2)
                        if (save_format == 'xlsx')|(save_format == 'xls'):
                            total_path = os.path.join(path, self.ticker.upper()+ '.' + save_format)
                            total_path = str(total_path)
                            writer = pd.ExcelWriter(total_path, engine = 'xlsxwriter')
                            final_df.to_excel(writer,
                                              sheet_name = self.ticker.upper() + ' OptionChain',
                                              freeze_panes = (3,2))
                            writer.close()
                        elif(save_format == 'csv')|(save_format == 'txt'):
                            final_df.to_csv(os.path.join(path, self.ticker.upper()+ '.' + save_format))
                        print('File Saved')
                    elif not os.path.exists(path):
                        print("Path doesn't exist. Creating directory")
                        sleep(2)
                        os.makedirs(path)
                        print('Saving data in {}'.format(str(path)))
                        sleep(2)
                        if (save_format == 'xlsx')|(save_format == 'xls'):
                            total_path = os.path.join(path, self.ticker.upper()+ '.' + save_format)
                            total_path = str(total_path)
                            writer = pd.ExcelWriter(total_path, engine = 'xlsxwriter')
                            final_df.to_excel(writer,
                                              sheet_name = self.ticker.upper() + ' OptionChain',
                                              freeze_panes = (3, 2))
                            writer.close()
                        elif(save_format == 'csv')|(save_format == 'txt'):
                            final_df.to_csv(os.path.join(path, self.ticker.upper()+ '.' + save_format))
                        print('File Saved')
                    return(str(path))
                else:
                    print('Folder name should be string')

            else:
                pass
        else:
            print('\n\n')
            print(final_df)



#%%
def main():
    flag = 0
    print("Module to get NASDAQ options data.\n\nLet's start with inputting the tickers.")
    tickers = [x.upper() for x in input().split()]
    print('Your tickers are:\n')
    print(*tickers, sep = '\n')
    print('\n\n')
    save_opt = input('Do you want to save File? [y/n]:  ')
    if save_opt == 'y':
        save = True
        folder_opt = input("What is the folder name you want to save the files in?\nIf you are running this file\
 on desktop and want to save it on a relative drectory\nfor example Desktop/Options/Optionchain,\
 type Options/Optionchain\n\n\n")
        folder = folder_opt
        format_opt = input('What format do you want to save the file in?\nAvailable options are "xslx",\
 "xls","csv", "txt": ')
        save_format = format_opt
        flag = 1

    elif save_opt == 'n':
        save = False
        folder = None
        save_format = 'xlsx'
        flag = 1
    else:
        return('Please choose from y or n')

    if (save_format == 'xlsx')|(save_format == 'xls')|(save_format == 'csv')|(save_format == 'txt'):
        pass
    else:
        return('File extension not supported, Please try again')

    if flag == 1:
        bar = tqdm(tickers, total = len(tickers), unit = 'Ticker')
        for i in bar:
            # tqdm.write("Getting options data for {}".format(i))
            bar.set_description('Option Chain for {}'.format(i.upper()),
                                refresh = True)
            sleep(2)
            start = NQOptions(i)
            path = start.get_options_data(save = save, folder = folder, save_format = save_format)

        print("You're all done")
        if save:
            print('Files are saved in {}'.format(str(path)))
    elif flag == 0:
        return('Input Error, please try again')


#%%
if __name__ == '__main__':
    main()
