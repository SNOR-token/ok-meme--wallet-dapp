import tkinter as tk
from tkinter import ttk, messagebox
import axiom
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base58
import requests
import json
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import asyncio

class OkMemeWalletApp:
    def __init__(self, master):
        self.master = master
        master.title("OK-MEME-WALLET")
        master.geometry("800x600")
        master.configure(bg="#FFD700")  # Gold background

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 12), borderwidth=1, relief="raised", background="#FF69B4", foreground="white")
        style.map('TButton', background=[('active', '#FF1493')])
        style.configure('TLabel', font=('Arial', 12), background="#FFD700", foreground="#4B0082")
        style.configure('TEntry', font=('Arial', 12))

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tron_frame = ttk.Frame(self.notebook, style='TFrame')
        self.solana_frame = ttk.Frame(self.notebook, style='TFrame')

        self.notebook.add(self.tron_frame, text="Tron Wallet")
        self.notebook.add(self.solana_frame, text="Solana Wallet")

        self.setup_tron_wallet()
        self.setup_solana_wallet()

        self.solana_client = AsyncClient("https://api.mainnet-beta.solana.com")

    def setup_tron_wallet(self):
        self.tron_private_key = None
        self.tron_public_key = None
        self.tron_address = None

        ttk.Button(self.tron_frame, text="Create Tron Wallet", command=self.create_tron_wallet).pack(pady=10)

        self.tron_address_label = ttk.Label(self.tron_frame, text="Tron Address: ")
        self.tron_address_label.pack(pady=5)

        self.tron_balance_label = ttk.Label(self.tron_frame, text="Tron Balance: ")
        self.tron_balance_label.pack(pady=5)

        ttk.Label(self.tron_frame, text="Recipient Address:").pack(pady=5)
        self.tron_recipient_entry = ttk.Entry(self.tron_frame)
        self.tron_recipient_entry.pack(pady=5)

        ttk.Label(self.tron_frame, text="Amount (TRX):").pack(pady=5)
        self.tron_amount_entry = ttk.Entry(self.tron_frame)
        self.tron_amount_entry.pack(pady=5)

        ttk.Button(self.tron_frame, text="Send TRX", command=self.send_trx).pack(pady=10)

    def setup_solana_wallet(self):
        self.solana_public_key = None

        ttk.Button(self.solana_frame, text="Connect to Solflare", command=self.connect_solflare).pack(pady=10)

        self.solana_address_label = ttk.Label(self.solana_frame, text="Solana Address: ")
        self.solana_address_label.pack(pady=5)

        self.solana_balance_label = ttk.Label(self.solana_frame, text="Solana Balance: ")
        self.solana_balance_label.pack(pady=5)

        ttk.Label(self.solana_frame, text="From Token:").pack(pady=5)
        self.from_token_entry = ttk.Entry(self.solana_frame)
        self.from_token_entry.pack(pady=5)

        ttk.Label(self.solana_frame, text="To Token:").pack(pady=5)
        self.to_token_entry = ttk.Entry(self.solana_frame)
        self.to_token_entry.pack(pady=5)

        ttk.Label(self.solana_frame, text="Amount:").pack(pady=5)
        self.swap_amount_entry = ttk.Entry(self.solana_frame)
        self.swap_amount_entry.pack(pady=5)

        ttk.Button(self.solana_frame, text="Swap Tokens", command=self.swap_tokens).pack(pady=10)

    def create_tron_wallet(self):
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        self.tron_private_key = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )

        self.tron_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        self.tron_address = self.public_key_to_tron_address(self.tron_public_key)
        self.tron_address_label.config(text=f"Tron Address: {self.tron_address}")
        self.update_tron_balance()

    def public_key_to_tron_address(self, public_key):
        address = b'\x41' + axiom.utils.keccak(public_key)[-20:]
        return base58.b58encode_check(address).decode()

    def update_tron_balance(self):
        if self.tron_address:
            try:
                response = requests.get(f"https://api.trongrid.io/v1/accounts/{self.tron_address}")
                data = response.json()
                balance = int(data['data'][0]['balance']) / 1_000_000  # Convert SUN to TRX
                self.tron_balance_label.config(text=f"Tron Balance: {balance} TRX")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch Tron balance: {str(e)}")

    def send_trx(self):
        if not self.tron_private_key:
            messagebox.showerror("Error", "Please create a Tron wallet first")
            return

        recipient = self.tron_recipient_entry.get()
        amount = self.tron_amount_entry.get()

        if not recipient or not amount:
            messagebox.showerror("Error", "Please enter recipient address and amount")
            return

        try:
            amount = int(float(amount) * 1_000_000)  # Convert TRX to SUN
            messagebox.showinfo("Info", f"Sending {amount/1_000_000} TRX to {recipient}")
            # Placeholder for actual transaction logic
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send transaction: {str(e)}")

    async def connect_solflare(self):
        # Async method to fetch Solana public key and balance
        try:
            self.solana_public_key = "DummySolanaPublicKey123456789"
            self.solana_address_label.config(text=f"Solana Address: {self.solana_public_key}")
            await self.update_solana_balance()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Solflare: {str(e)}")

    async def update_solana_balance(self):
        if self.solana_public_key:
            try:
                balance = await self.solana_client.get_balance(self.solana_public_key, commitment=Confirmed)
                balance = balance['result']['value'] / 1_000_000_000  # Convert lamports to SOL
                self.solana_balance_label.config(text=f"Solana Balance: {balance} SOL")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch Solana balance: {str(e)}")

    async def swap_tokens(self):
        if not self.solana_public_key:
            messagebox.showerror("Error", "Please connect to Solflare first")
            return

        from_token = self.from_token_entry.get()
        to_token = self.to_token_entry.get()
        amount = self.swap_amount_entry.get()

        if not from_token or not to_token or not amount:
            messagebox.showerror("Error", "Please enter all swap details")
            return

        try:
            # Placeholder for Jupiter (jup.ag) swap logic
            messagebox.showinfo("Info", f"Swapping {amount} {from_token} to {to_token}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to swap tokens: {str(e)}")

def run_app():
    root = tk.Tk()
    app = OkMemeWalletApp(root)
    root.mainloop()

if __name__ == "__main__":
    asyncio.run(run_app())
