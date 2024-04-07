import { Transaction } from 'bitcoinjs-lib';
import { Networks, OutputType } from 'boltz-core';
import { EventEmitter } from 'events';
import Logger from '../../../lib/Logger';
import { SwapType, SwapUpdateEvent } from '../../../lib/consts/Enums';
import ChannelCreation from '../../../lib/db/models/ChannelCreation';
import ReverseSwap from '../../../lib/db/models/ReverseSwap';
import Swap from '../../../lib/db/models/Swap';
import { ChainSwapInfo } from '../../../lib/db/repositories/ChainSwapRepository';
import EventHandler from '../../../lib/service/EventHandler';
import SwapNursery from '../../../lib/swap/SwapNursery';
import { Currency } from '../../../lib/wallet/WalletManager';
import { generateAddress } from '../../Utils';

class StubEventEmitter extends EventEmitter {
  constructor() {
    super();
  }

  public emit = (event: string, ...args: any[]): boolean => {
    return super.emit(event, ...args);
  };
}

const swap = {
  id: 'id',
  acceptZeroConf: true,
  type: SwapType.Submarine,
  status: SwapUpdateEvent.SwapCreated,
} as Swap;

const channelCreation = {
  fundingTransactionId: 'fundingId',
  fundingTransactionVout: 43,
} as ChannelCreation;

const reverseSwap = {
  id: 'reverseId',
  type: SwapType.ReverseSubmarine,
  status: SwapUpdateEvent.TransactionMempool,
} as ReverseSwap;

const chainSwap = {
  id: 'chainSwapId',
  type: SwapType.Chain,
} as ChainSwapInfo;

const mockTransaction = () => {
  const { outputScript } = generateAddress(OutputType.Bech32);
  const transaction = new Transaction();

  transaction.addOutput(outputScript, 1);

  return transaction;
};

describe('EventHandler', () => {
  const symbol = 'BTC';

  const currencies = new Map<string, Currency>([
    [
      symbol,
      {
        symbol,
        chainClient: {} as any,
        lndClient: new StubEventEmitter() as any,
        network: Networks.bitcoinRegtest,
      } as any as Currency,
    ],
  ]);

  const nursery = new StubEventEmitter();
  (nursery as any).channelNursery = new StubEventEmitter();

  const eventHandler = new EventHandler(
    Logger.disabledLogger,
    currencies,
    nursery as any,
  );

  beforeEach(() => {
    eventHandler.removeAllListeners();
    jest.clearAllMocks();
  });

  test('should emit on swap creation', () => {
    expect.assertions(2);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({ status: SwapUpdateEvent.SwapCreated });
    });

    eventHandler.emitSwapCreation(swap.id);
  });

  test('should emit on invoice set', () => {
    expect.assertions(2);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({ status: SwapUpdateEvent.InvoiceSet });
    });

    eventHandler.emitSwapInvoiceSet(swap.id);
  });

  test.each`
    confirmed
    ${false}
    ${true}
  `(
    'should emit on submarine swap transactions (confirmed: $confirmed)',
    ({ confirmed }) => {
      expect.assertions(2);

      eventHandler.once('swap.update', ({ id, status }) => {
        expect(id).toEqual(swap.id);
        expect(status).toEqual({
          status: confirmed
            ? SwapUpdateEvent.TransactionConfirmed
            : SwapUpdateEvent.TransactionMempool,
        });
      });

      nursery.emit('transaction', {
        swap,
        confirmed,
        transaction: mockTransaction(),
      });
    },
  );

  test('should emit on Bitcoin style transactions', () => {
    expect.assertions(2);

    const transaction = mockTransaction();

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(reverseSwap.id);
      expect(status).toEqual({
        status: SwapUpdateEvent.TransactionMempool,
        transaction: {
          id: transaction.getId(),
          hex: transaction.toHex(),
        },
      });
    });

    nursery.emit('transaction', {
      transaction,
      swap: reverseSwap,
      confirmed: false,
    });
  });

  test('should emit on Ethereum style transactions', () => {
    expect.assertions(2);

    const transactionHash = 'txHash';

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(reverseSwap.id);
      expect(status).toEqual({
        status: SwapUpdateEvent.TransactionMempool,
        transaction: {
          id: transactionHash,
        },
      });
    });

    nursery.emit('transaction', {
      swap: reverseSwap,
      confirmed: false,
      transaction: transactionHash,
    });
  });

  test('should emit on invoice settlement', () => {
    expect.assertions(3);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(reverseSwap.id);
      expect(status).toEqual({ status: SwapUpdateEvent.InvoiceSettled });
    });
    eventHandler.once('swap.success', (args) => {
      expect(args.swap).toEqual(reverseSwap);
    });

    nursery.emit('invoice.settled', reverseSwap);
  });

  test('should emit on invoice pending', () => {
    expect.assertions(2);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({ status: SwapUpdateEvent.InvoicePending });
    });

    nursery.emit('invoice.pending', swap);
  });

  test('should emit when invoice could not be paid', () => {
    expect.assertions(3);

    const failureReason = 'no';
    const toEmit = { ...swap, failureReason };

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({
        failureReason,
        status: SwapUpdateEvent.InvoiceFailedToPay,
      });
    });
    eventHandler.once('swap.failure', (args) => {
      expect(args).toEqual({
        swap: toEmit,
        reason: failureReason,
      });
    });

    nursery.emit('invoice.failedToPay', toEmit);
  });

  test('should emit when invoice is paid', () => {
    expect.assertions(2);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({ status: SwapUpdateEvent.InvoicePaid });
    });

    nursery.emit('invoice.paid', swap);
  });

  test('should emit when invoice expired', () => {
    expect.assertions(2);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({ status: SwapUpdateEvent.InvoiceExpired });
    });

    nursery.emit('invoice.expired', swap);
  });

  test('should emit when 0-conf transactions are rejected', () => {
    expect.assertions(2);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({
        zeroConfRejected: true,
        status: SwapUpdateEvent.TransactionMempool,
      });
    });

    nursery.emit('zeroconf.rejected', swap);
  });

  test('should emit on submarine swap claims', () => {
    expect.assertions(3);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({ status: SwapUpdateEvent.TransactionClaimed });
    });
    eventHandler.once('swap.success', (args) => {
      expect(args).toEqual({ swap, channelCreation });
    });

    nursery.emit('claim', { swap, channelCreation });
  });

  test('should emit on chain swap claims', () => {
    expect.assertions(3);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(chainSwap.id);
      expect(status).toEqual({ status: SwapUpdateEvent.TransactionClaimed });
    });
    eventHandler.once('swap.success', (args) => {
      expect(args).toEqual({ swap: chainSwap });
    });

    nursery.emit('claim', { swap: chainSwap });
  });

  test('should emit on pending claims', () => {
    expect.assertions(2);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({
        status: SwapUpdateEvent.TransactionClaimPending,
      });
    });

    nursery.emit('claim.pending', swap);
  });

  test('should emit when swap expires', () => {
    expect.assertions(3);

    const failureReason = 'expired';
    const toEmit = { ...swap, failureReason };

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({
        failureReason,
        status: SwapUpdateEvent.SwapExpired,
      });
    });
    eventHandler.once('swap.failure', (args) => {
      expect(args).toEqual({
        swap: toEmit,
        reason: failureReason,
      });
    });

    nursery.emit('expiration', toEmit);
  });

  test('should emit when miner fee is paid', () => {
    expect.assertions(2);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({
        status: SwapUpdateEvent.MinerFeePaid,
      });
    });

    nursery.emit('minerfee.paid', swap);
  });

  test('should emit when Bitcoin like coins are sent', () => {
    expect.assertions(2);

    const transaction = mockTransaction();

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(reverseSwap.id);
      expect(status).toEqual({
        status: SwapUpdateEvent.TransactionMempool,
        transaction: {
          id: transaction.getId(),
          hex: transaction.toHex(),
          eta: SwapNursery.reverseSwapMempoolEta,
        },
      });
    });

    nursery.emit('coins.sent', {
      transaction,
      swap: reverseSwap,
    });
  });

  test('should emit when Ethereum like coins are sent', () => {
    expect.assertions(2);

    const transactionHash = 'mockTransaction';

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(reverseSwap.id);
      expect(status).toEqual({
        status: SwapUpdateEvent.TransactionMempool,
        transaction: {
          id: transactionHash,
        },
      });
    });

    nursery.emit('coins.sent', {
      swap: reverseSwap,
      transaction: transactionHash,
    });
  });

  test('should emit when onchain coins could not be sent', () => {
    expect.assertions(3);

    const failureReason = 'no funds';
    const toEmit = { ...swap, failureReason };

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({
        failureReason,
        status: SwapUpdateEvent.TransactionFailed,
      });
    });
    eventHandler.once('swap.failure', (args) => {
      expect(args).toEqual({
        swap: toEmit,
        reason: failureReason,
      });
    });

    nursery.emit('coins.failedToSend', toEmit);
  });

  test('should emit when onchain coins are refunded', () => {
    expect.assertions(3);

    const failureReason = 'refunded';
    const toEmit = { ...swap, failureReason };

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({
        failureReason,
        status: SwapUpdateEvent.TransactionRefunded,
      });
    });
    eventHandler.once('swap.failure', (args) => {
      expect(args).toEqual({
        swap: toEmit,
        reason: failureReason,
      });
    });

    nursery.emit('refund', { swap: toEmit });
  });

  test('should emit on channel creation', () => {
    expect.assertions(2);

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({
        status: SwapUpdateEvent.ChannelCreated,
        channel: {
          fundingTransactionId: channelCreation.fundingTransactionId,
          fundingTransactionVout: channelCreation.fundingTransactionVout,
        },
      });
    });

    (nursery as any).channelNursery.emit('channel.created', {
      swap,
      channelCreation,
    });
  });

  test('should emit when lockup fails', () => {
    expect.assertions(2);

    const failureReason = 'too little';
    const toEmit = { ...swap, failureReason };

    eventHandler.once('swap.update', ({ id, status }) => {
      expect(id).toEqual(swap.id);
      expect(status).toEqual({
        failureReason,
        status: SwapUpdateEvent.TransactionLockupFailed,
      });
    });

    nursery.emit('lockup.failed', toEmit);
  });

  test('should emit on channel backup', () => {
    expect.assertions(2);

    const backup = 'data';

    eventHandler.once('channel.backup', ({ currency, channelBackup }) => {
      expect(symbol).toEqual(currency);
      expect(channelBackup).toEqual(backup);
    });

    currencies.get(symbol)!.lndClient!.emit('channel.backup', backup);
  });
});
