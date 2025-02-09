import os
import json
from web3 import Web3

def load_abi(file_path: str):
    """Load the ABI JSON file from the given file path."""
    with open(file_path, "r") as file:
        return json.load(file)

# Determine the current directory and the path to the ABI file.
current_dir = os.path.dirname(os.path.abspath(__file__))
abi_file_path = os.path.join(current_dir, "vault_factory_abi.json")
VAULT_FACTORY_ABI = load_abi(abi_file_path)

class VaultFactoryClient:
    def __init__(self, rpc_url, factory_address, deployer_private_key):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.factory_address = Web3.to_checksum_address(factory_address)
        self.deployer_private_key = deployer_private_key
        self.account = self.web3.eth.account.from_key(deployer_private_key)
        self.factory_contract = self.web3.eth.contract(
            address=self.factory_address,
            abi=VAULT_FACTORY_ABI
        )

    def deploy_vault(self, agent_address, user_address):
        agent = Web3.to_checksum_address(agent_address)
        user = Web3.to_checksum_address(user_address)
        txn = self.factory_contract.functions.deployVault(agent, user).buildTransaction({
            'from': self.account.address,
            'nonce': self.web3.eth.get_transaction_count(self.account.address),
            'gas': 3000000,
            'gasPrice': self.web3.toWei('20', 'gwei')
        })
        signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.deployer_private_key)
        txn_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash)
        if receipt.status != 1:
            raise Exception("Vault deployment transaction failed")
        # Process the event to obtain the new vault address.
        events = self.factory_contract.events.VaultDeployed().processReceipt(receipt)
        if not events:
            raise Exception("VaultDeployed event not found")
        vault_address = events[0]['args']['vaultAddress']
        return vault_address 