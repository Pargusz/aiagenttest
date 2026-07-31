#!/usr/bin/env python3
"""ParguszPhysics baslatici.

Kullanim:
    python3 run.py                 # arayuzu ac + ogrenmeye basla
    python3 run.py --port 9000     # farkli port
    python3 run.py --ogrenme-yok   # ogrenme motoru kapali baslat
    python3 run.py --sadece-ogren  # arayuz acmadan sadece ogren (gunlerce)
    python3 run.py --sor "soru"    # terminalden tek soru sor
    python3 run.py --test          # kendini test et
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import config, db  # noqa: E402


def main():
    ap = argparse.ArgumentParser(
        prog="parguszphysics",
        description="ParguszPhysics — fizik, hesaplama ve MATLAB asistani")
    ap.add_argument("--port", type=int, default=config.PORT)
    ap.add_argument("--host", default=config.HOST)
    ap.add_argument("--ogrenme-yok", action="store_true",
                    help="ogrenme motorunu baslatma")
    ap.add_argument("--tarayici-yok", action="store_true",
                    help="tarayiciyi otomatik acma")
    ap.add_argument("--sadece-ogren", action="store_true",
                    help="arayuz acmadan sadece ogrenme motorunu calistir")
    ap.add_argument("--sor", metavar="SORU",
                    help="terminalden tek bir soru sor ve cik")
    ap.add_argument("--test", action="store_true", help="kendini test et")
    args = ap.parse_args()

    db.init()
    # Daha once ogrenilmis soru ifadelerini arama tabanina kat
    from core import formulas as _formuller, genisleme as _genisleme
    _formuller.ogrenilenleri_bagla()
    # Makalelerden uretilmis yol haritalarini ve turetilmis formulleri yukle
    _genisleme.haritalari_bagla()
    _genisleme.formulleri_bagla()

    if args.test:
        from core import selftest
        return selftest.run()

    if args.sor:
        from core import brain
        r = brain.respond(args.sor, session="terminal")
        print()
        print(r.text)
        print()
        return 0

    if args.sadece_ogren:
        from core import learner
        import time
        learner.LEARNER.start()
        print("\n  ParguszPhysics — ogrenme kipi")
        print("  Durdurmak icin Ctrl+C\n")
        try:
            while True:
                time.sleep(30)
                s = db.stats()
                print("  makale: %-9s kavram: %-7s baglanti: %-8s terim: %-8s | %s"
                      % ("{:,}".format(s["makale"]), "{:,}".format(s["kavram"]),
                         "{:,}".format(s["baglanti"]), "{:,}".format(s["terim"]),
                         s["durum"]))
        except KeyboardInterrupt:
            learner.LEARNER.stop()
            print("\n  Durduruldu.\n")
        return 0

    from core import server
    server.serve(host=args.host, port=args.port,
                 open_browser=not args.tarayici_yok,
                 start_learning=not args.ogrenme_yok)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
