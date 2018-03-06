from boa_test.tests.boa_test import BoaFixtureTest
from boa.compiler import Compiler
from neo.Core.TX.Transaction import Transaction
from neo.Prompt.Commands.BuildNRun import TestBuild
from neo.EventHub import events
from neo.SmartContract.SmartContractEvent import SmartContractEvent, NotifyEvent
from neo.Settings import settings
from neo.Prompt.Utils import parse_param
from neo.Core.FunctionCode import FunctionCode
from neocore.Fixed8 import Fixed8
from boa_test.example.demo.nex.token import *

import shutil
import os

settings.USE_DEBUG_STORAGE = True
settings.DEBUG_STORAGE_PATH = './fixtures/debugstorage'


class TestContract(BoaFixtureTest):

    dispatched_events = []
    dispatched_logs = []

    @classmethod
    def tearDownClass(cls):
        super(BoaFixtureTest, cls).tearDownClass()

        try:
            if os.path.exists(settings.DEBUG_STORAGE_PATH):
                shutil.rmtree(settings.DEBUG_STORAGE_PATH)
        except Exception as e:
            print("couldn't remove debug storage %s " % e)

    @classmethod
    def setUpClass(cls):
        super(TestContract, cls).setUpClass()

        cls.dirname = '/'.join(os.path.abspath(__file__).split('/')[:-2])

        def on_notif(evt):
            print(evt)
            cls.dispatched_events.append(evt)
            print("dispatched events %s " % cls.dispatched_events)

        def on_log(evt):
            print(evt)
            cls.dispatched_logs.append(evt)
        events.on(SmartContractEvent.RUNTIME_NOTIFY, on_notif)
        events.on(SmartContractEvent.RUNTIME_LOG, on_log)

    def test_ICOTemplate_1(self):

        output = Compiler.instance().load('%s/ico_template.py' % TestContract.dirname).default
        out = output.write()
#        print(output.to_s())

        tx, results, total_ops, engine = TestBuild(out, ['name', '[]'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetString(), TOKEN_NAME)

        tx, results, total_ops, engine = TestBuild(out, ['symbol', '[]'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetString(), TOKEN_SYMBOL)

        tx, results, total_ops, engine = TestBuild(out, ['decimals', '[]'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), TOKEN_DECIMALS)

        tx, results, total_ops, engine = TestBuild(out, ['totalSupply', '[]'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 0)

        tx, results, total_ops, engine = TestBuild(out, ['nonexistentmethod', '[]'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetString(), 'unknown operation')

        # deploy with wallet 2 should fail CheckWitness
        tx, results, total_ops, engine = TestBuild(out, ['deploy', '[]'], self.GetWallet2(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        tx, results, total_ops, engine = TestBuild(out, ['deploy', '[]'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), True)

        # second time, it should already be deployed and return false
        tx, results, total_ops, engine = TestBuild(out, ['deploy', '[]'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        # now total supply should be equal to the initial owner amount
        tx, results, total_ops, engine = TestBuild(out, ['totalSupply', '[]'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), TOKEN_INITIAL_AMOUNT)

        # now the owner should have a balance of the TOKEN_INITIAL_AMOUNT
        tx, results, total_ops, engine = TestBuild(out, ['balanceOf', parse_param([bytearray(TOKEN_OWNER)])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), TOKEN_INITIAL_AMOUNT)

    def test_ICOTemplate_2(self):

        output = Compiler.instance().load('%s/ico_template.py' % TestContract.dirname).default
        out = output.write()

        # now transfer tokens to wallet 2

        TestContract.dispatched_events = []

        test_transfer_amount = 2400000001
        tx, results, total_ops, engine = TestBuild(out, ['transfer', parse_param([bytearray(TOKEN_OWNER), self.wallet_2_script_hash.Data, test_transfer_amount])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), True)

        self.assertEqual(len(TestContract.dispatched_events), 1)
        evt = TestContract.dispatched_events[0]
        self.assertIsInstance(evt, NotifyEvent)
        self.assertEqual(evt.addr_from.Data, bytearray(TOKEN_OWNER))
        self.assertEqual(evt.addr_to, self.wallet_2_script_hash)
        self.assertEqual(evt.amount, test_transfer_amount)

        # now get balance of wallet 2
        tx, results, total_ops, engine = TestBuild(out, ['balanceOf', parse_param([self.wallet_2_script_hash.Data])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), test_transfer_amount)

        # now the owner should have less
        tx, results, total_ops, engine = TestBuild(out, ['balanceOf', parse_param([bytearray(TOKEN_OWNER)])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), TOKEN_INITIAL_AMOUNT - test_transfer_amount)

        # now this transfer should fail
        tx, results, total_ops, engine = TestBuild(out, ['transfer', parse_param([bytearray(TOKEN_OWNER), self.wallet_2_script_hash.Data, TOKEN_INITIAL_AMOUNT])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        # this transfer should fail because it is not signed by the 'from' address
        tx, results, total_ops, engine = TestBuild(out, ['transfer', parse_param([bytearray(TOKEN_OWNER), self.wallet_2_script_hash.Data, 10000])], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        # now this transfer should fail, this is from address with no tokens
        tx, results, total_ops, engine = TestBuild(out, ['transfer', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data, 1000])], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        # get balance of bad data
        tx, results, total_ops, engine = TestBuild(out, ['balanceOf', parse_param(['abc'])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 0)

        # get balance no params
        tx, results, total_ops, engine = TestBuild(out, ['balanceOf', parse_param([])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

    def test_ICOTemplate_3_KYC(self):

        output = Compiler.instance().load('%s/ico_template.py' % TestContract.dirname).default
        out = output.write()
        print(output.to_s())
        # now transfer tokens to wallet 2

        TestContract.dispatched_events = []

        # test mint tokens without being kyc verified
        tx, results, total_ops, engine = TestBuild(out, ['mintTokens', '[]', '--attach-neo=10'], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        # Try to register as a non owner
        tx, results, total_ops, engine = TestBuild(out, ['crowdsale_register', parse_param([self.wallet_3_script_hash.Data])], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        # Get status of non registered address
        tx, results, total_ops, engine = TestBuild(out, ['crowdsale_status', parse_param([self.wallet_3_script_hash.Data])], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        TestContract.dispatched_events = []

        # register an address
        tx, results, total_ops, engine = TestBuild(out, ['crowdsale_register', parse_param([self.wallet_3_script_hash.Data])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 1)

        # it should dispatch an event
        self.assertEqual(len(TestContract.dispatched_events), 1)
        evt = TestContract.dispatched_events[0]
        self.assertEqual(evt.event_payload[0], b'kyc_registration')

        # register 2 addresses at once
        tx, results, total_ops, engine = TestBuild(out, ['crowdsale_register', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 2)

        # now check reg status
        tx, results, total_ops, engine = TestBuild(out, ['crowdsale_status', parse_param([self.wallet_3_script_hash.Data])], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), True)

    def test_ICOTemplate_4_attachments(self):

        output = Compiler.instance().load('%s/ico_template.py' % TestContract.dirname).default
        out = output.write()

        # test mint tokens without being kyc verified
        tx, results, total_ops, engine = TestBuild(out, ['get_attachments', '[]', '--attach-neo=10'], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        attachments = results[0].GetArray()
        self.assertEqual(len(attachments), 4)

        fn = FunctionCode(out, '0705', '05')

        self.assertEqual(attachments[0].GetByteArray(), fn.ScriptHash().Data)
        self.assertEqual(attachments[1].GetByteArray(), self.wallet_3_script_hash.Data)
        self.assertEqual(attachments[2].GetBigInteger(), Fixed8.FromDecimal(10).value)
        self.assertEqual(attachments[3].GetBigInteger(), 0)

        tx, results, total_ops, engine = TestBuild(out, ['get_attachments', '[]'], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        attachments = results[0].GetArray()
        self.assertEqual(len(attachments), 4)

        self.assertEqual(attachments[1].GetByteArray(), bytearray())
        self.assertEqual(attachments[2].GetBigInteger(), 0)
        self.assertEqual(attachments[3].GetBigInteger(), 0)

        tx, results, total_ops, engine = TestBuild(out, ['get_attachments', '[]', '--attach-neo=3', '--attach-gas=3.12'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        attachments = results[0].GetArray()
        self.assertEqual(len(attachments), 4)
        self.assertEqual(attachments[1].GetByteArray(), self.wallet_1_script_hash.Data)
        self.assertEqual(attachments[2].GetBigInteger(), Fixed8.FromDecimal(3).value)
        self.assertEqual(attachments[3].GetBigInteger(), Fixed8.FromDecimal(3.12).value)

    def test_ICOTemplate_5_mint(self):

        output = Compiler.instance().load('%s/ico_template.py' % TestContract.dirname).default
        out = output.write()

        # register an address
        tx, results, total_ops, engine = TestBuild(out, ['crowdsale_register', parse_param([self.wallet_3_script_hash.Data])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 1)

        TestContract.dispatched_events = []

        # test mint tokens, this should return true
        tx, results, total_ops, engine = TestBuild(out, ['mintTokens', '[]', '--attach-neo=10'], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), True)

        # it should dispatch an event
        self.assertEqual(len(TestContract.dispatched_events), 1)
        evt = TestContract.dispatched_events[0]
        self.assertIsInstance(evt, NotifyEvent)
        self.assertEqual(evt.amount, 10 * TOKENS_PER_NEO)
        self.assertEqual(evt.addr_to, self.wallet_3_script_hash)

        # test mint tokens again, this should be false since you can't do it twice
        tx, results, total_ops, engine = TestBuild(out, ['mintTokens', '[]', '--attach-neo=10'], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        # now the minter should have a balance
        tx, results, total_ops, engine = TestBuild(out, ['balanceOf', parse_param([self.wallet_3_script_hash.Data])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 10 * TOKENS_PER_NEO)

        # now the total circulation should be bigger
        tx, results, total_ops, engine = TestBuild(out, ['totalSupply', '[]'], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), (10 * TOKENS_PER_NEO) + TOKEN_INITIAL_AMOUNT)

    def test_ICOTemplate_6_approval(self):

        output = Compiler.instance().load('%s/ico_template.py' % TestContract.dirname).default
        out = output.write()

        # tranfer_from, approve, allowance
        tx, results, total_ops, engine = TestBuild(out, ['allowance', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data])], self.GetWallet2(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 0)

        # try to transfer from
        tx, results, total_ops, engine = TestBuild(out, ['transferFrom', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data, 10000])], self.GetWallet2(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        # try to approve from someone not yourself
        tx, results, total_ops, engine = TestBuild(out, ['approve', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data, 10000])], self.GetWallet2(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 0)

        # try to approve more than you have
        tx, results, total_ops, engine = TestBuild(out, ['approve', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data, TOKEN_INITIAL_AMOUNT])], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 0)

        TestContract.dispatched_events = []

        # approve should work
        tx, results, total_ops, engine = TestBuild(out, ['approve', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data, 1234])], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), True)

        # it should dispatch an event
        self.assertEqual(len(TestContract.dispatched_events), 1)
        evt = TestContract.dispatched_events[0]
        self.assertIsInstance(evt, NotifyEvent)
        self.assertEqual(evt.notify_type, b'approve')
        self.assertEqual(evt.amount, 1234)

        # check allowance
        tx, results, total_ops, engine = TestBuild(out, ['allowance', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data])], self.GetWallet2(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 1234)

        # approve should not be additive, it should overwrite previous approvals
        tx, results, total_ops, engine = TestBuild(out, ['approve', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data, 133234])], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), True)

        tx, results, total_ops, engine = TestBuild(out, ['allowance', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data])], self.GetWallet2(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 133234)

        # now you can transfer from
        tx, results, total_ops, engine = TestBuild(out, ['transferFrom', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data, 10000])], self.GetWallet2(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), True)

        # now the recevier should have a balance
        # it is equal to 10000 plus test_transfer_amount = 2400000001

        tx, results, total_ops, engine = TestBuild(out, ['balanceOf', parse_param([self.wallet_2_script_hash.Data])], self.GetWallet1(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 10000 + 2400000001)

        # now the allowance should be less
        tx, results, total_ops, engine = TestBuild(out, ['allowance', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data])], self.GetWallet2(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBigInteger(), 133234 - 10000)

        # try to transfer too much, even with approval
        tx, results, total_ops, engine = TestBuild(out, ['transferFrom', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data, 14440000])], self.GetWallet2(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)

        # cant approve negative amounts
        tx, results, total_ops, engine = TestBuild(out, ['approve', parse_param([self.wallet_3_script_hash.Data, self.wallet_2_script_hash.Data, -1000])], self.GetWallet3(), '0705', '05')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetBoolean(), False)
