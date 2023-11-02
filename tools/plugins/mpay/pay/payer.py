from time import perf_counter
from typing import Any

from pyln.client import Millisatoshi, Plugin
from sqlalchemy.orm import Session

from plugins.mpay.data.network_info import NetworkInfo
from plugins.mpay.data.route_stats import RouteStats
from plugins.mpay.data.router import Router
from plugins.mpay.db.helpers import insert_failed_attempt, insert_successful_attempt
from plugins.mpay.db.models import Payment
from plugins.mpay.pay.channels import ChannelsHelper, NoRouteError
from plugins.mpay.pay.route import Route
from plugins.mpay.pay.sendpay import PaymentError, PaymentHelper, PaymentResult
from plugins.mpay.utils import fee_with_percent

_MAX_HOPS = 5


class PaymentTimeoutError(Exception):
    pass


class Payer:
    _pl: Plugin

    _router: Router
    _pay: PaymentHelper
    _channels: ChannelsHelper
    _network_info: NetworkInfo

    _session: Session
    _payment: Payment

    _bolt11: str
    _dec: dict[str, Any]
    _amount: Millisatoshi

    _max_fee: Millisatoshi
    _timeout: int

    _start_time: float

    def __init__(
        self,
        pl: Plugin,
        router: Router,
        pay: PaymentHelper,
        channel: ChannelsHelper,
        network_info: NetworkInfo,
        session: Session,
        payment: Payment,
        bolt11: str,
        dec: dict[str, Any],
        max_fee: Millisatoshi,
        timeout: int,
    ) -> None:
        self._pl = pl

        self._router = router
        self._pay = pay
        self._channels = channel
        self._network_info = network_info

        self._session = session
        self._payment = payment

        self._bolt11 = bolt11
        self._dec = dec
        self._amount = dec["amount_msat"]

        self._max_fee = max_fee
        self._timeout = timeout

    # TODO: check direct channels first (implicitly by increasing maxhops in queryroutes)
    # TODO: save exclude list of temporarily disabled channels
    def start(
        self,
    ) -> PaymentResult:
        self._start_time = perf_counter()

        exclude_list = self._channels.get_channel_exclude_list(self._amount)

        self._pl.log("Fetching known routes")
        for stats, route in self._router.fetch_routes(self._dec, self._amount, exclude_list):
            res = self._send_payment(
                route,
                stats,
                exclude_list,
            )
            if res is not None:
                return res

            self._check_timeout()

        for max_hops in range(2, _MAX_HOPS + 1):
            try:
                for route in self._channels.get_route(self._dec, exclude_list, max_hops):
                    res = self._send_payment(
                        route,
                        None,
                        exclude_list,
                    )
                    if res is not None:
                        return res

                    self._check_timeout()

            except NoRouteError:  # noqa: PERF203
                # Continue in the loop incrementing the max hops
                continue

        raise NoRouteError

    def _send_payment(
        self,
        route: Route,
        stats: RouteStats | None,
        exclude_list: list[str],
    ) -> PaymentResult | None:
        if route.exceeds_fee(self._max_fee):
            # TODO: exclude most expensive channel
            self._pl.log(
                f"Not attempting route {route.pretty_print(self._network_info)}: "
                f"fee {fee_with_percent(self._amount, route.fee)} exceeds budget"
            )
            return None

        route.add_cltv(self._dec["min_final_cltv_expiry"])
        self._pl.log(
            f"Attempting route for {self._payment.payment_hash} with fee "
            f"{fee_with_percent(self._amount, route.fee)}: "
            f"{route.pretty_print(self._network_info)}"
            f"{f' {stats.pretty_statistics}' if stats is not None else ''}"
        )

        try:
            res = self._pay.send(route, self._bolt11, self._dec)
        except PaymentError as e:
            exclude_list.append(f"{e.erring_channel}/{e.erring_direction}")
            insert_failed_attempt(self._session, self._payment, route, e)
            raise

        insert_successful_attempt(self._session, self._payment, route, res.time)

        res.time = self._time_elapsed
        self._pl.log(
            f"Paid {self._payment.payment_hash} "
            f"with fee {fee_with_percent(self._amount, res.fee_msat)} "
            f"in {res.time}s via: {route.pretty_print(self._network_info)}"
        )

        return res

    @property
    def _time_elapsed(self) -> int:
        return round(perf_counter() - self._start_time)

    def _check_timeout(self) -> None:
        if self._time_elapsed > self._timeout:
            raise PaymentTimeoutError
