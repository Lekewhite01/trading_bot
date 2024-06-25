import pandas as pd
from trading_ig import IGService
from tenacity import Retrying, wait_exponential, retry_if_exception_type
from trading_ig.rest import ApiExceededException

DEFAULT_RETRY = Retrying(
    wait=wait_exponential(), retry=retry_if_exception_type(ApiExceededException)
)

# Get environment login variables and assign to python variables in config file
import trading_ig_config

def IG_connect():
    # Connect to IGService
    ig_service = IGService(
        trading_ig_config.config.username,
        trading_ig_config.config.password,
        trading_ig_config.config.api_key,
        trading_ig_config.config.acc_type,
    )

    ig_service.create_session()

    # print(ig_service.create_session())
    # Print account details
    account = ig_service.fetch_accounts()
    print("Account_ID:", account.accountId)
    return ig_service

def display_top_level_nodes():
    ig_service = IG_connect()
    response = ig_service.fetch_top_level_navigation_nodes()
    df = response["nodes"]
    df = df[(df["name"]=='Forex') | (df["name"]=='Indices') | \
            (df["name"]=='Commodities Metals Energies') | (df["name"]=='Commodities Metals Energies (mini)') | \
            (df["name"]=='Shares - US (All Sessions)')]
    return df

def display_subnodes(node_id=0, space="", ig_service=None):
    if ig_service is None:
        ig_service = IG_connect()

    sub_nodes = ig_service.fetch_sub_nodes_by_node(node_id)
    # print(sub_nodes)
    if sub_nodes["nodes"].shape[0] != 0:
        rows = sub_nodes["nodes"].to_dict("records")
        print(rows)
        df = pd.DataFrame(rows)
        return df
    
def display_sectors(node_id=0, space="", ig_service=None):
    if ig_service is None:
        ig_service = IG_connect()
        
    sub_nodes = ig_service.fetch_sub_nodes_by_node(node_id)
    
    all_cols = []

    if sub_nodes["nodes"].shape[0] != 0:
        rows = sub_nodes["nodes"].to_dict("records")
        for record in rows:
            print(f"{space}{record['name']} [{record['id']}]")
            # Collect columns from recursive call
            sub_cols = display_sectors(
                record["id"], space=space + "  ", ig_service=ig_service
            )
            all_cols.extend(sub_cols)

    if sub_nodes["markets"].shape[0] != 0:
        cols = sub_nodes["markets"].to_dict("records")
        all_cols.extend(cols)
    return all_cols

def main():
    top_level_df = display_top_level_nodes()
    print(top_level_df)
    while True:
        try:
            node_id = int(input("Enter the node ID to explore or 'q' to quit: ").strip())
        except ValueError:
            print("Invalid input. Please enter a valid node ID or 'q' to quit.")
            continue
        
        if node_id == 'q':
            break

        print(display_subnodes(node_id=node_id))

        subnode_id = int(input("Enter the sub-node ID to explore or 'q' to quit: ").strip())
        sectors = display_sectors(node_id=subnode_id)
        sector_df = pd.DataFrame(sectors)[["epic", "instrumentName"]]
        print(sector_df)
        repeat = input("Do you want to explore another node? (y/n): ").strip().lower()
        if repeat != 'y':
            break

if __name__ == "__main__":
    main()
