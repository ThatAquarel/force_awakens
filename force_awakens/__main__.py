import argparse

import force_awakens.app as app
import force_awakens.web.server as web

from multiprocessing import Process, Queue


def main():
    parser = argparse.ArgumentParser(
        prog="The Force Awakens",
        description="2024 McGill Physics Hackathon, Dawson College",
    )

    parser.add_argument("-w", "--web", action="store_true")
    parser.add_argument("-p", "--port", default=8080)
    args = parser.parse_args()

    # args.web = True

    if args.web:
        vec_queue = Queue()

        web_proc = Process(
            target=web.server_process,
            args=(vec_queue,),
            daemon=True,
        )
        web_proc.start()

        import ngrok
        import qrcode

        listener = ngrok.connect(args.port, authtoken_from_env=True)
        print(f"Ingress established at {listener.url()}")

        img = qrcode.make(listener.url())
        app.run(
            args.web,
            qr=img,
            vec_queue=vec_queue,
        )
    else:
        app.run(args.web)


if __name__ == "__main__":
    main()
