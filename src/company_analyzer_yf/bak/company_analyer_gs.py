import os
from gs_quant.markets.securities import SecurityMaster
from gs_quant.session import GsSession

class AssetAnalyzer:
    def __init__(self, symbol):
        """
        Initialize the AssetAnalyzer with the ticker symbol.
        
        Args:
        - symbol (str): Company symbol (e.g., 'AAPL' for Apple).
        """
        self.is_etf = None
        self.is_stock = None
        self.symbol = symbol
        self.asset = None
        self.session = None
        self._setup_gs_session()

    def _setup_gs_session(self):
        """
        Set up the GsSession using client ID and client secret from environment variables.
        """
        client_id = os.getenv('gsquant-clientid')
        client_secret = os.getenv('gsquant-clientsecret')
        if client_id and client_secret:
            self.session = GsSession.get_external_session(client_id=client_id, client_secret=client_secret)
        else:
            raise ValueError("Missing client ID or client secret in environment variables")

    def _get_asset_info(self):
        """
        Retrieve asset information (like name and ID) from SecurityMaster.
        """
        # If self.asset is empty, retrieve info using SecurityMaster.get_asset
        if not self.asset:
            self.asset = SecurityMaster.get_asset(self.symbol)

    def get_metric(self, metric_name):
        """
        Get a specific financial metric for the company.
        
        Args:
        - metric_name (str): Name of the metric to retrieve (e.g., 'PE_RATIO', 'MARKET_CAP', 'DIVIDEND_YIELD').
        
        Returns:
        - float or None: Value of the metric if available, None otherwise.
        """
        self._get_asset_info()
        return self.asset.get_metric(metric_name)

    def get_all_metrics(self):
        """
        Get all available financial metrics for the company.
        
        Returns:
        - dict: Dictionary containing all available metrics and their values.
        """
        self._get_asset_info()
        metrics = self.asset.get_all_metrics()
        return metrics

# Example usage:
if __name__ == "__main__":
    # Instantiate the CompanyAnalyzer with a symbol
    analyzer = AssetAnalyzer('AAPL')  # Example: Apple Inc.

    # Retrieve and print various metrics
    print(f"Company Name: {analyzer.name()}")
    print(f"Company Symbol: {analyzer.symbol()}")
    print(f"P/E Ratio: {analyzer.get_metric('PE_RATIO')}")
    print(f"Market Cap: {analyzer.get_metric('MARKET_CAP')}")
    print(f"Dividend Yield: {analyzer.get_metric('DIVIDEND_YIELD')}")
    print(f"All Metrics: {analyzer.get_all_metrics()}")
