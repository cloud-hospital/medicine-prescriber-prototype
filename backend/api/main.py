""" Module for command line interface (cli). """

import json
import os

from . import config, document_db, lib, machine_learning, oauth2

# region user


def _update_user_profile(user_profile, user_info) -> None:
    if not "name" in user_profile or user_profile["name"].strip() == "":
        user_profile["name"] = user_info.name
    else:
        user_profile["name"] = ""
    user_profile["login_sub"] = user_info.login_sub
    if (
        not "picture_url" in user_profile is None
        or user_profile["picture_url"].strip() == ""
    ):
        user_profile["picture_url"] = user_info.picture_url
    else:
        user_profile["picture_url"] = ""
    if (
        not "profile_url" in user_profile is None
        or user_profile["profile_url"].strip() == ""
    ):
        user_profile["profile_url"] = user_info.profile_url
    else:
        user_profile["profile_url"] = ""
    user_profile["last_logged_in"] = user_info.last_logged_in
    document_db.upsert_user(user_profile)


def get_access_token(authorisation_code) -> str:
    """Get access token using authorisation code."""
    access_token = oauth2.get_access_token(authorisation_code)
    obj = json.loads(access_token)
    user_info = oauth2.get_user_info(obj["access_token"])
    if user_info:
        user_profile = document_db.get_user(user_info.email_address)
        if not user_profile:
            return "Error: user is not registered to access!"
        _update_user_profile(user_profile, user_info)
        return access_token
    return None


def validate_access_token(token, claims) -> bool:
    """Validate access token and verify claims."""
    return oauth2.validate_access_token(token, claims)


def get_user_profile(email_address) -> str:
    user_profile = document_db.get_user(email_address)
    if not user_profile:
        return "Error: user is not registered to access!"
    return user_profile


# endregion

# region symptoms to causes


def read_all_subjective_symptoms() -> list[str]:
    """Read all subjective symptoms."""
    return document_db.read_all_subjective_symptoms()


def read_all_associated_symptoms() -> list[str]:
    """Read all associated symptoms."""
    return document_db.read_all_associated_symptoms()


def read_all_gender() -> list[str]:
    """Read all gender values."""
    return document_db.read_all_gender()


def read_all_age_groups() -> list[str]:
    """Read all age groups."""
    return document_db.read_all_age_groups()


def read_all_investigations() -> list[str]:
    """Read all investigations."""
    return document_db.read_all_investigations()


def predict_provisional_diagnosis(
    subjective_symptoms, associated_symptoms, investigations_done, gender, age
) -> list[(str, float)]:
    """Predict provisional diagnosis from symptoms."""
    return machine_learning.predict_provisional_diagnosis(
        subjective_symptoms, associated_symptoms, investigations_done, gender, age
    )


def read_advises(provisional_diagnosis) -> list[str]:
    """Read advised investigations, management and surgical management."""
    return document_db.read_advises(provisional_diagnosis)


# endregion

# region data scrapper


def read_doctor_raw_data_links(profile_link) -> list[str]:
    """Read doctor raw data links."""
    return document_db.read_doctor_raw_data_links(profile_link)


def read_doctor_raw_data(question_detail_link) -> list[str]:
    """Read doctor raw data."""
    return document_db.read_doctor_raw_data(question_detail_link)


def read_doctor_processed_data(question_detail_link) -> list[str]:
    """Read doctor processed data."""
    return document_db.read_doctor_processed_data(question_detail_link)


# endregion


def init() -> None:
    """Entry point if called as an executable."""
    cli_args = lib.parse_cli_args()
    config.DEBUG_MODE = cli_args.debug_mode
    config.PORT = cli_args.port
    config.MODEL_FILE = os.environ.get("MODEL_FILE", default=config.MODEL_FILE)
    config.SYMPTOMS_TOKENISER_FILE = os.environ.get(
        "SYMPTOMS_TOKENISER_FILE", default=config.SYMPTOMS_TOKENISER_FILE
    )
    config.CAUSES_TOKENISER_FILE = os.environ.get(
        "CAUSES_TOKENISER_FILE", default=config.CAUSES_TOKENISER_FILE
    )
    config.SYMPTOMS_SEPARATOR = os.environ.get(
        "SYMPTOMS_SEPARATOR", default=config.SYMPTOMS_SEPARATOR
    )
    config.SYMPTOMS_SEQUENCE_PADDING_TYPE = os.environ.get(
        "SYMPTOMS_SEQUENCE_PADDING_TYPE", default=config.SYMPTOMS_SEQUENCE_PADDING_TYPE
    )
    config.SYMPTOMS_SEQUENCE_MAXLEN = os.environ.get(
        "SYMPTOMS_SEQUENCE_MAXLEN", default=config.SYMPTOMS_SEQUENCE_MAXLEN
    )
    config.MONGODB_URL = os.environ.get("MONGODB_URL", default=config.MONGODB_URL)
    config.MONGODB_DATABASE = os.environ.get(
        "MONGODB_DATABASE", default=config.MONGODB_DATABASE
    )
    config.WEB_REQUEST_TIMEOUT_SECONDS = os.environ.get(
        "WEB_REQUEST_TIMEOUT_SECONDS", default=config.WEB_REQUEST_TIMEOUT_SECONDS
    )
    config.CACHE_TIMEOUT_SECONDS = os.environ.get(
        "CACHE_TIMEOUT_SECONDS", default=config.CACHE_TIMEOUT_SECONDS
    )
    config.TENANT_DOMAIN = os.environ.get("TENANT_DOMAIN", default=config.TENANT_DOMAIN)
    config.TENANT_OPENID_CONFIGURATION_CACHE_KEY = os.environ.get(
        "TENANT_OPENID_CONFIGURATION_CACHE_KEY",
        default=config.TENANT_OPENID_CONFIGURATION_CACHE_KEY,
    )
    config.AUTHORISATION_HEADER_KEY = os.environ.get(
        "AUTHORISATION_HEADER_KEY", default=config.AUTHORISATION_HEADER_KEY
    )
    config.REDIRECT_URL = os.environ.get("REDIRECT_URL", default=config.REDIRECT_URL)
    config.CLIENT_ID = os.environ.get("CLIENT_ID", default=config.CLIENT_ID)
    config.CLIENT_SECRET = os.environ.get("CLIENT_SECRET", default=config.CLIENT_SECRET)

    lib.configure_global_logging_level()
    lib.log_config_settings()

    machine_learning.configure()
    document_db.configure_mongodb_client()
    # document_db.log_mongodb_status()
    oauth2.init_cache_state()


if __name__ == "__main__":
    init()
