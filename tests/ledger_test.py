"""
Test case for Ledger
"""
import unittest
from ledger import Itau
from ledger import Nubank


class TestLedger(unittest.TestCase):
    """
    Test ledgers
    """

    def setUp(self):
        """
        Setup test
        """
        self._itau = Itau(None)
        self._nubank = Nubank(None)

    def test_new_entry_itau(self):
        """
        Test new entry itau
        """
        with open("./tests/fixture/itau.csv", 'r') as csv_file:
            self._itau.read_file(csv_file)
            csv_file.close()

        self.assertEqual(self._itau.list_entry()[0].desc, 'RSHOP-CENTER CAST')
        self.assertEqual(self._itau.list_entry()[1].desc, 'RSHOP-H2O DISTRIB')
        self.assertEqual(self._itau.list_entry()[2].desc,
                         '(#422) INT PAG TIT BANCO')
        self.assertEqual(self._itau.list_entry()[3].desc,
                         '(#0100317) INT TIM CELULAR')
        self.assertEqual(
            self._itau.list_entry()[4].desc,
            'REMUNERACAO/SALARIO')
        self.assertEqual(self._itau.list_entry()[5].desc, '(#06920987) TBI')
        self.assertEqual(self._itau.list_entry()[6].desc,
                         'REND PAGO APLIC AUT MAIS')
        self.assertEqual(self._itau.list_entry()[7].desc,
                         'RSHOP-ELETRO ELET')
        self.assertEqual(
            self._itau.list_entry()[8].desc,
            'REMUNERACAO/SALARIO')
        self.assertEqual(self._itau.list_entry()[9].desc, 'CXE')

    def test_new_entry_nubank(self):
        """
        Test new entry nubank
        """
        with open("./tests/fixture/nubank.csv", 'r') as csv_file:
            self._nubank.read_file(csv_file)
            csv_file.close()

        self.assertEqual(
            self._nubank.list_entry()[0].desc, 'Auto Posto Piratininga')
        self.assertEqual(self._nubank.list_entry()[1].desc, 'Lojas Americanas')
        self.assertEqual(self._nubank.list_entry()[2].desc, 'Netflix.Com')
        self.assertEqual(self._nubank.list_entry()[6].desc, 'Poli Pet')
        self.assertEqual(
            self._nubank.list_entry()[7].desc,
            'Pagamento recebido')
