from flask import redirect, request, session, current_app
from flask_appbuilder.security.manager import AUTH_OID
from superset.security import SupersetSecurityManager
from flask_oidc import OpenIDConnect
from flask_appbuilder.security.views import AuthOIDView
from flask_login import login_user, logout_user, current_user
from urllib.parse import quote
from flask_appbuilder.views import expose
import urllib.parse
import logging
import jwt
from .pyjwt import FilteredPyJWKClient


logger = logging.getLogger(__name__)

OIDC_SID_KEY = "oidc-sid"


class OIDCSecurityManager(SupersetSecurityManager):

    def __init__(self, appbuilder):
        super(OIDCSecurityManager, self).__init__(appbuilder)
        logger.info(
            f"Mise en place de notre security manager custom nommé OIDCSecurityManager"
        )
        if self.auth_type == AUTH_OID:
            self.oid = OpenIDConnect(self.appbuilder.get_app)
        else:
            logger.error(
                f"Veuillez mettre le configuration AUTH_TYPE = AUTH_OID dans superset_config.py"
            )
        self.authoidview = AuthOIDCView

        self.jwkclient = FilteredPyJWKClient(self.oid.client_secrets["jwks_uri"])

        self.sid_to_disconnect = []
        """List de session id à deconnecter."""

    def push_sid_to_disconnect(self, sid: str):
        logger.debug(f"Push sid {sid} to be disconnected.")
        self.sid_to_disconnect.append(sid)

    def pop_sid_to_disconnect(self, sid: str):
        if sid in self.sid_to_disconnect:
            self.sid_to_disconnect.remove(sid)
            logger.debug(f"Pop sid {sid} to be disconnected.")
            return sid
        return None


class AuthOIDCView(AuthOIDView):

    @expose("/login/", methods=["GET", "POST"])
    def login(self, flag=True):
        sm = self.appbuilder.sm
        oidc = sm.oid

        @self.appbuilder.sm.oid.require_login
        def handle_login():
            user = sm.auth_user_oid(oidc.user_getfield("email"))

            info = oidc.user_getinfo(
                ["preferred_username", "given_name", "family_name", "email"]
            )

            # _username, _firstname, _lastname, _email, _sid = \
            #     oidc.user_getinfo(['preferred_username', 'given_name', 'family_name', 'email']).values()

            if user is None:
                user = sm.add_user(
                    info.get("preferred_username"),
                    info.get("given_name"),
                    info.get("family_name"),
                    info.get("email"),
                    [],
                )
                logger.info(
                    f"Création de l'utilisateur {info.get('preferred_username')} dans superset"
                )

                logger.info(f"Application des roles à l'utilisateur {user.username}")
                default_role = current_app.config.get(
                    "CUSTOM_AUTH_USER_REGISTRATION_ROLE", "Public"
                )
                self._attach_roles_for(user, default_roles=[default_role])
                sm.update_user(user)
            else:
                logger.info(f"Connexion de l'utilisateur {user.username}")

            login_user(user, remember=False, force=True)
            session[OIDC_SID_KEY] = info.get("_sid")
            return redirect(self.appbuilder.get_url_for_index)

        return handle_login()

    @expose("/logout/", methods=["GET", "POST"])
    def logout(self):
        oidc = self.appbuilder.sm.oid

        oidc.logout()
        super(AuthOIDCView, self).logout()
        redirect_url = urllib.parse.quote_plus(request.url_root.strip("/"))

        return redirect(
            oidc.client_secrets.get("issuer")
            + "/protocol/openid-connect/logout?client_id="
            + oidc.client_secrets.get("client_id")
        )

    @expose("/sso-logout/", methods=["GET", "POST"])
    def sso_logout(self):
        """Back channel logout. Flag la session à être déconnectée par sa session id oidc"""
        logger.debug(f"SSO logout a été appelé")
        sm: OIDCSecurityManager = self.appbuilder.sm
        oidc = sm.oid
        clientid = oidc.client_secrets["client_id"]

        logout_jwt = request.form["logout_token"]

        try:
            payload = self._decode_logout_jwt(logout_jwt, clientid)
        except jwt.ExpiredSignatureError as e:
            msg = f"Le jeton de deconnexion est expiré"
            logger.exception(msg, exc_info=e)
            return 400, msg
        except jwt.DecodeError as e:
            msg = f"Le jeton de deconnexion est invalide"
            logger.exception(msg, exc_info=e)
            return 400, msg

        logout_sid = payload["sid"]

        sm.push_sid_to_disconnect(logout_sid)
        msg = f"On flag la session {logout_sid} pour deconnexion"
        logger.info(f"On flag la session {logout_sid} pour deconnexion")
        return msg

    def _decode_logout_jwt(self, token: str, aud: str) -> dict:
        """Décode un jeton jwt en vérifiant la signature"""
        sm: OIDCSecurityManager = self.appbuilder.sm

        signing_key = sm.jwkclient.get_signing_key_from_jwt(token)

        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=aud,
            options={"verify_exp": False},
        )
        return decoded

    def _attach_roles_for(self, user, default_roles: list[str] = None):
        """
        Attache les roles fournis dans le token d'authentification à l'utilisateur superset local.
        Applique automatiquement les roles par défaut
        """
        sm = self.appbuilder.sm
        oidc = self.appbuilder.sm.oid

        if default_roles is None:
            default_roles = []

        lookfor_roles = [
            "admin",
            "alpha",
            "gamma",
            "public",
        ]  # roles supportés par notre adapter
        token_info_roles: dict = oidc.user_getinfo(["roles"])

        token_roles = default_roles
        if "roles" in token_info_roles:
            token_roles = token_info_roles["roles"] + token_roles

        roles_to_apply = self._intersection_insensible_casse(lookfor_roles, token_roles)
        logger.debug(f"Application des roles {roles_to_apply} à {user}")

        roles = []
        for role in roles_to_apply:
            found = sm.find_role(role.capitalize())
            if found is None:
                logger.warning(
                    f"Role {role} not found in superset. It will be overlooked!"
                )
                continue
            roles.append(found)

        user.roles = roles

    def _intersection_insensible_casse(
        self, lst1: list[str], lst2: list[str]
    ) -> list[str]:
        """Intersection entre deux list de str (insensible à la casse)"""
        upper2 = [x.upper() for x in lst2]
        intersection = [v for v in lst1 if v.upper() in upper2]
        return intersection


def oidc_check_loggedin_or_logout():
    """
    Vérifie que l'utilisateur est loggé via le module OIDC
    Si ce n'est pas le cas, deconnexion de la session courante

    Conçu pour être utilisé avec @app.before_request
    """
    from superset import security_manager as sm

    oidc = sm.oid if sm else None
    sm: OIDCSecurityManager = sm

    if oidc is None:
        return

    curr_sid = session[OIDC_SID_KEY] if OIDC_SID_KEY in session else None
    curr_to_disconnect = sm.pop_sid_to_disconnect(curr_sid) is not None

    if not oidc.user_loggedin or curr_to_disconnect:
        if current_user.is_authenticated:
            logger.warning(
                f"Utilisateur {current_user} déconnecté de keycloak. On deconnecte la session."
            )
            oidc.logout()
            logout_user()
