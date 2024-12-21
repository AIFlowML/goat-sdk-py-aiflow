import { Tool } from "@goat-sdk/core";
import { SolanaWalletClient } from "@goat-sdk/wallet-solana";
import { createJupiterApiClient } from "@jup-ag/api";
import { ComputeBudgetProgram, PublicKey, Transaction, TransactionInstruction } from "@solana/web3.js";

import { GetQuoteParameters } from "./parameters";

export class JupiterService {
    private readonly jupiterApiClient: ReturnType<typeof createJupiterApiClient>;

    constructor() {
        this.jupiterApiClient = createJupiterApiClient();
    }

    @Tool({
        description: "Get a quote for a swap on the Jupiter DEX",
    })
    async getQuote(parameters: GetQuoteParameters) {
        try {
            const response = this.jupiterApiClient.quoteGet(parameters);
            return response;
        } catch (error: unknown) {
            if (error && typeof error === "object" && "response" in error) {
                const response = error.response as Response;

                const result = await response.json();
                throw new Error(`Failed to get quote: ${result.error}`);
            }
            throw error;
        }
    }

    @Tool({
        description: "Swap an SPL token for another token on the Jupiter DEX",
    })
    async swapTokens(walletClient: SolanaWalletClient, parameters: GetQuoteParameters) {
        const quoteResponse = await this.getQuote(parameters);

        const { swapTransaction } = await this.jupiterApiClient.swapPost({
            swapRequest: {
                userPublicKey: walletClient.getAddress(),
                quoteResponse: quoteResponse,
                dynamicComputeUnitLimit: true,
                prioritizationFeeLamports: "auto",
            },
        });

        const versionedTransaction = VersionedTransaction.deserialize(Buffer.from(swapTransaction, "base64"));
        const instructions = await decompileVersionedTransactionToInstructions(
            walletClient.getConnection(),
            versionedTransaction,
        );

        const { hash } = await walletClient.sendTransaction({
            instructions,
            addressLookupTableAddresses: versionedTransaction.message.addressTableLookups.map((lookup) =>
                lookup.accountKey.toBase58(),
            ),
        });

        return {
            hash,
        };
    }
}

import { type DecompileArgs, TransactionMessage } from "@solana/web3.js";

import { type Connection, VersionedTransaction } from "@solana/web3.js";

export async function decompileVersionedTransactionToInstructions(
    connection: Connection,
    versionedTransaction: VersionedTransaction,
) {
    const lookupTableAddresses = versionedTransaction.message.addressTableLookups.map((lookup) => lookup.accountKey);
    const addressLookupTableAccounts = await Promise.all(
        lookupTableAddresses.map((address) =>
            connection.getAddressLookupTable(address).then((lookupTable) => lookupTable.value),
        ),
    );
    const nonNullAddressLookupTableAccounts = addressLookupTableAccounts.filter((lookupTable) => lookupTable != null);
    const decompileArgs: DecompileArgs = {
        addressLookupTableAccounts: nonNullAddressLookupTableAccounts,
    };
    return TransactionMessage.decompile(versionedTransaction.message, decompileArgs).instructions;
}