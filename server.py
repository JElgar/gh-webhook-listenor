import hmac
import json
import logging
from flask import Flask, abort, request
from subprocess import PIPE, Popen
from os import getenv, access, X_OK, listdir
from os.path import join
from sys import stderr, exit
from typing import Optional, Tuple

app = Flask(__name__)
webhook_secret = getenv("GH_WEBHOOK_SECRET")

logging.basicConfig(stream=stderr, level=logging.INFO)

hooks_dir = getenv("WEBHOOK_HOOKS_DIR", "/app/hooks")
scripts = [join(hooks_dir, file) for file in sorted(listdir(hooks_dir))]
if not scripts:
    logging.error(
        "No executable hook scripts found; did you forget to"
        " mount something into %s or chmod +x them?",
        hooks_dir,
    )
    exit(1)


def get_hook(event: str) -> Optional[str]:
    return next(
        (script for script in scripts if script == f"{hooks_dir}/{event}.sh"), None
    )


def run_hook(event: str) -> Tuple[str, str]:
    script = get_hook(event)
    if script:
        proc = Popen([script], stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        out = out.decode("utf-8")
        err = err.decode("utf-8")

        if proc.returncode != 0:
            logging.error("[%s]: %d\n%s", script, proc.returncode, err)
        else:
            logging.info("[%s]: %d\n%s", script, proc.returncode, out)

        return out, err
    else:
        logging.error("Failed to find script")


@app.route("/", methods=["POST"])
def gh_webhooks():

    # == Verify secret == #
    # Taken from https://github.com/staticfloat/docker-webhook

    # Get signature from the webhook request
    header_signature = request.headers.get("X-Hub-Signature")
    header_gitlab_token = request.headers.get("X-Gitlab-Token")
    if header_signature is not None:
        # Construct an hmac, abort if it doesn't match
        try:
            sha_name, signature = header_signature.split("=")
        except:
            logging.info(
                "X-Hub-Signature format is incorrect (%s), aborting", header_signature
            )
            abort(400)
        data = request.get_data()
        try:
            mac = hmac.new(webhook_secret.encode("utf8"), msg=data, digestmod=sha_name)
        except:
            logging.info(
                "Unsupported X-Hub-Signature type (%s), aborting", header_signature
            )
            abort(400)
        if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
            logging.info(
                "Signature did not match (%s and %s), aborting",
                str(mac.hexdigest()),
                str(signature),
            )
            abort(403)
        event = request.headers.get("X-GitHub-Event", "ping")
    elif header_gitlab_token is not None:
        if webhook_secret != header_gitlab_token:
            logging.info("Gitlab Secret Token did not match, aborting")
            abort(403)
        event = request.headers.get("X-Gitlab-Event", "unknown")
    else:
        logging.info("X-Hub-Signature was missing, aborting")
        abort(403)

    # == Handle events == #

    if event == "ping":
        return json.dumps({"msg": "pong"})

    else:
        run_hook(event)


if __name__ == "__main__":
    host_url = getenv("HOST_URL", "0.0.0.0")
    host_port = getenv("HOST_PORT", 8000)
    logging.info(
        f"All systems operational, beginning application loop. Host: {host_url}, Port: {host_port}"
    )
    app.run(debug=False, host=host_url, port=host_port)
