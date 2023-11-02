from pyln.client import Millisatoshi, Plugin
from sqlalchemy.orm import Session

from plugins.mpay.data.network_info import NetworkInfo
from plugins.mpay.data.route_stats import RouteStatsFetcher
from plugins.mpay.data.router import Router
from plugins.mpay.db.db import Database
from plugins.mpay.db.models import Payment
from plugins.mpay.pay.channels import ChannelsHelper
from plugins.mpay.pay.payer import Payer
from plugins.mpay.pay.sendpay import PaymentHelper, PaymentResult
from plugins.mpay.utils import fee_with_percent, format_error


class MPay:
    default_max_fee_perc: float = 0.05

    _pl: Plugin
    _db: Database

    _router: Router
    _pay: PaymentHelper
    _channels: ChannelsHelper
    _network_info: NetworkInfo

    def __init__(self, pl: Plugin, db: Database, route_stats: RouteStatsFetcher) -> None:
        self._pl = pl
        self._db = db

        self._pay = PaymentHelper(pl)
        self._network_info = NetworkInfo(pl)
        self._channels = ChannelsHelper(pl)
        self._router = Router(pl, route_stats, self._network_info)

    def pay(self, bolt11: str, max_fee: int | None, exempt_fee: int, timeout: int) -> PaymentResult:
        with Session(self._db.engine) as session:
            dec = self._pl.rpc.decodepay(bolt11)

            amount = dec["amount_msat"]
            payment_hash = dec["payment_hash"]

            payment = Payment(
                destination=dec["payee"], payment_hash=payment_hash, amount=int(amount)
            )
            session.add(payment)
            session.commit()

            max_fee = self._calculate_fee(amount, max_fee, exempt_fee)
            self._pl.log(
                f"Paying {payment_hash} for {amount} with max fee "
                f"{fee_with_percent(dec['amount_msat'], max_fee)}"
            )

            try:
                return Payer(
                    self._pl,
                    self._router,
                    self._pay,
                    self._channels,
                    self._network_info,
                    session,
                    payment,
                    bolt11,
                    dec,
                    max_fee,
                    timeout,
                ).start()
            except BaseException as e:
                if payment.ok or payment.ok is None:
                    payment.ok = False
                    session.commit()

                self._pl.log(f"Payment {payment_hash} failed: {format_error(e)}", level="warn")

                raise

    def _calculate_fee(
        self, amount: Millisatoshi, max_fee: int | None, exempt_fee: int
    ) -> Millisatoshi:
        if max_fee is not None:
            return Millisatoshi(max_fee)

        calculated = Millisatoshi(round((int(amount) * self.default_max_fee_perc) / 100))
        self._pl.log(f"Calculated default max fee of {calculated}")

        exemption = Millisatoshi(exempt_fee)
        if calculated < exemption:
            self._pl.log(f"Using exempt fee of {exemption}")
            return exemption

        return calculated
