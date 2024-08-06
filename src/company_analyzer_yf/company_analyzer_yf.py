import yfinance as yf
import time
import logging
from colorama import Fore, Style, Back, init
import json
import os

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(filename='asset_monitor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AssetMonitor:
    def __init__(self, symbols):
        """
        Initialize the AssetMonitor with a list of ticker symbols.
        
        Args:
        - symbols (list of str): List of company/ETF symbols (e.g., ['AAPL', 'MSFT']).
        """
        self.symbols = symbols
        self.data = {}
        self.update_data()
        self.print_header()

    def update_data(self):
        """
        Fetch data for all symbols and update self.data.
        """
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                
                # Get historical data for the last 5 days
                history_data = ticker.history(period='5d')
                
                # Get other financial metrics. Everything is contained into the ticker.info data structure
                info = ticker.info
                currency = info.get('currency', '')
                current_price = info.get('currentPrice', None)
                pe_ratio = info.get('trailingPE', None)
                eps = info.get('trailingEps', None)
                dividend_yield = info.get('dividendYield', None)
                if isinstance(dividend_yield, (int, float)):
                    dividend_yield *= 100  # Convert to percentage
                
                # Get current price and calculate percent change
                prev_close = history_data['Close'].iloc[-2] if len(history_data) > 1 else None
                
                if isinstance(current_price, (int, float)) and isinstance(prev_close, (int, float)) and prev_close != 0:
                    percent_change = ((current_price - prev_close) / prev_close * 100)
                else:
                    percent_change = None

                self.data[symbol] = {
                    'ticker_and_name': f"{symbol} ({info.get('shortName', 'N/A')})",
                    'currency': currency,
                    'currentPrice': f"{currency} {current_price:.2f}" if current_price else 'N/A',
                    'prevClose': f"{currency} {prev_close:.2f}" if prev_close else 'N/A',
                    'percentChange': percent_change,
                    'fiftyTwoWeekLow': f"{currency} {info.get('fiftyTwoWeekLow', None):.2f}" if info.get('fiftyTwoWeekLow', None) else 'N/A',
                    'fiftyTwoWeekHigh': f"{currency} {info.get('fiftyTwoWeekHigh', None):.2f}" if info.get('fiftyTwoWeekHigh', None) else 'N/A',
                    'peRatio': pe_ratio,
                    'epsTrailingTwelveMonths': eps,
                    'dividendYield': dividend_yield,
                    'marketCap': self.format_number(info.get('marketCap')) if info.get('marketCap') else 'N/A',
                    'industry': info.get('industry', 'N/A')
                }
                logging.info(f"Updated data for {symbol}")
            except Exception as e:
                logging.error(f"Error updating data for {symbol}: {str(e)}")
                self.data[symbol] = {'ticker_and_name': f"{symbol} (Error)", 'error': str(e)}

    def format_number(self, value):
        """
        Format large numbers for readability (e.g., in millions).
        
        Args:
        - value (float): The value to format.
        
        Returns:
        - str: Formatted number or 'N/A' if the value is not a number.
        """
        if isinstance(value, (int, float)):
            return "{:,.0f}M".format(value / 1e6)
        return 'N/A'

    def format_header(self, header, width):
        """
        Format the header to fit within the given width and break it into multiple lines if needed.
        
        Args:
        - header (str): The header text.
        - width (int): The width of the column.
        
        Returns:
        - str: Formatted header text with line breaks.
        """
        if len(header) > width:
            # Break header into two lines
            mid = width // 2
            first_line = header[:mid].strip()
            second_line = header[mid:].strip()
            return f"{first_line.center(width)}\n{second_line.center(width)}"
        else:
            return header.center(width)

    def print_header(self):
        """
        Print the table header.
        """
        # Define column widths
        self.col_width = {
            'Company Info': 35,
            'Prev Close': 15,
            'Current Price': 15,
            '% Change': 15,
            '52 Week Low': 15,
            '52 Week High': 15,
            'P/E Ratio': 10,
            'EPS': 10,
            'Dividend Yield': 15,
            'Market Cap': 15,
            'Industry': 20
        }
        
        # Define headers
        headers = [
            "Company Info", "Prev Close", "Current Price",
            "% Change", "52 Week Low", "52 Week High", "P/E Ratio", "EPS",
            "Dividend Yield", "Market Cap", "Industry"
        ]
        
        # Format headers
        formatted_headers = [
            Fore.CYAN + self.format_header(header, self.col_width[header]) + Style.RESET_ALL
            for header in headers
        ]
        
        # Print headers
        header_lines = [header.split('\n') for header in formatted_headers]
        max_lines = max(len(line) for line in header_lines)
        
        for i in range(max_lines):
            print(' '.join(
                (header_lines[j][i] if i < len(header_lines[j]) else ' ' * self.col_width[headers[j]]).ljust(self.col_width[headers[j]])
                for j in range(len(headers))
            ))
        
        print('-' * (sum(self.col_width.values()) + len(headers) - 1))

    def print_data(self):
        """
        Print updated data rows.
        """
        for symbol, info in self.data.items():
            percent_change = info.get('percentChange')
            if isinstance(percent_change, (int, float)):
                percent_change_str = f"{percent_change:.2f}%"
                # Determine background color based on percent change
                if percent_change < 0:
                    percent_change_str_colored = Fore.WHITE + Back.RED + percent_change_str + Style.RESET_ALL
                else:
                    percent_change_str_colored = Fore.WHITE + Back.GREEN + '+' + percent_change_str + Style.RESET_ALL
            else:
                percent_change_str_colored = Fore.WHITE + Back.BLACK + 'N/A' + Style.RESET_ALL

            dividend_yield = info.get('dividendYield')
            dividend_yield_str = f"{dividend_yield:.2f}%" if isinstance(dividend_yield, (int, float)) else 'N/A'

            # Convert numerical values to strings for formatting
            prev_close_str = info.get('prevClose', 'N/A')
            current_price_str = info.get('currentPrice', 'N/A')
            fifty_two_week_low_str = info.get('fiftyTwoWeekLow', 'N/A')
            fifty_two_week_high_str = info.get('fiftyTwoWeekHigh', 'N/A')
            pe_ratio_str = f"{info.get('peRatio', 'N/A'):.2f}" if isinstance(info.get('peRatio', None), (int, float)) else 'N/A'
            eps_str = f"{info.get('epsTrailingTwelveMonths', 'N/A'):.2f}" if isinstance(info.get('epsTrailingTwelveMonths', None), (int, float)) else 'N/A'
            market_cap_str = info.get('marketCap', 'N/A')
            industry_str = info.get('industry', 'N/A')

            row = [
                Fore.GREEN + (info.get('ticker_and_name', 'N/A')).center(self.col_width['Company Info']) + Style.RESET_ALL,
                Fore.MAGENTA + prev_close_str.center(self.col_width['Prev Close']) + Style.RESET_ALL,
                Fore.BLUE + current_price_str.center(self.col_width['Current Price']) + Style.RESET_ALL,
                percent_change_str_colored.center(self.col_width['% Change']),
                Fore.RED + fifty_two_week_low_str.center(self.col_width['52 Week Low']) + Style.RESET_ALL,
                Fore.CYAN + fifty_two_week_high_str.center(self.col_width['52 Week High']) + Style.RESET_ALL,
                Fore.CYAN + pe_ratio_str.center(self.col_width['P/E Ratio']) + Style.RESET_ALL,
                Fore.WHITE + eps_str.center(self.col_width['EPS']) + Style.RESET_ALL,
                Fore.LIGHTYELLOW_EX + dividend_yield_str.center(self.col_width['Dividend Yield']) + Style.RESET_ALL,
                Fore.LIGHTGREEN_EX + market_cap_str.center(self.col_width['Market Cap']) + Style.RESET_ALL,
                Fore.LIGHTMAGENTA_EX + industry_str.center(self.col_width['Industry']) + Style.RESET_ALL
            ]
            
            print(' '.join(row))


    def move_cursor_up(self, lines):
        """
        Move the cursor up by a given number of lines.
        
        Args:
        - lines (int): Number of lines to move the cursor up.
        """
        print(f"\033[{lines}A", end='')

    def monitor(self, interval=30):
        """
        Periodically update and print metrics at a given interval (in seconds).
        
        Args:
        - interval (int): Time between updates in seconds (default is 30 seconds).
        """
        try:
            self.print_header()  # Print header once
            while True:
                self.update_data()
                self.move_cursor_up(len(self.symbols) + 2)  # Move cursor up to overwrite the old data
                self.print_data()
                logging.info("Summary printed.")
                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user.")

# Example usage
if __name__ == "__main__":
    # Load symbols from the JSON file
    json_file_path = os.path.join(os.path.dirname(__file__), 'companies_list.json')
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Extract ticker symbols
    symbols = [company['symbol'] for company in data]

    # Create AssetMonitor instance
    monitor = AssetMonitor(symbols)  # Initialize with ticker symbols from the JSON file

    # Start monitoring with updates every 1 second
    monitor.monitor(interval=1)