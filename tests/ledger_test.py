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

        result = """2017-09-15 (#422) INT PAG TIT BANCO
    Assets:Checking                      -998.99 BRL
    Expenses:Unknown"""

        assert str(self._itau.list_entry()[2]) == result

        result = """2017-09-30 CXE
    Assets:Checking                      -100.00 BRL
    Expenses:Unknown"""

        assert str(self._itau.list_entry()[9]) == result

    def test_new_entry_nubank(self):
        """
        Test new entry nubank
        """
        with open("./tests/fixture/nubank.csv", 'r') as csv_file:
            self._nubank.read_file(csv_file)
            csv_file.close()

        result = """2017-09-11=2017-10-15 Netflix.Com
    Expenses:Unknown                       27.90 BRL
    Liabilities:Nubank"""

        self.assertEqual(str(self._nubank.list_entry()[2]), result)

        result = """2017-09-15=2017-10-15 Pagamento recebido
    Expenses:Unknown                     -998.99 BRL
    Liabilities:Nubank"""

        self.assertEqual(str(self._nubank.list_entry()[7]), result)
