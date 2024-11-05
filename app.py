from shiny import App, ui, reactive, render
import os
import base64
import hashlib
import secrets
import requests
import pkce

from shiny import App, ui, reactive, render

app_ui = ui.page_fluid(
    ui.h2("Browse OneDrive Files with ShinyLive"),
    ui.tags.button("Sign In to OneDrive", onclick="signIn()"),
    ui.output_text_verbatim("access_token_output"),
    ui.tags.script(src="https://alcdn.msauth.net/browser/2.35.0/js/msal-browser.min.js"),
    ui.tags.script("""
        const msalConfig = {
            auth: {
                clientId: "00c96c03-65b7-4885-beda-3d16874133a0",
                authority: "https://login.microsoftonline.com/9798e3e4-0f1a-4f96-91ad-b31a4229413a",
                redirectUri: "https://localhost:8000/",
            },
            cache: {
                cacheLocation: "localStorage",
                storeAuthStateInCookie: false,
            },
            system: {
                navigateToLoginRequestUrl: false,
            },
        };

        const msalInstance = new msal.PublicClientApplication(msalConfig);
        const loginRequest = {
            scopes: ["Files.Read.All", "User.Read"],
        };

        function signIn() {
            msalInstance.loginPopup(loginRequest)
                .then(loginResponse => {
                    msalInstance.setActiveAccount(loginResponse.account);
                    getTokenPopup(loginRequest)
                        .then(tokenResponse => {
                            const accessToken = tokenResponse.accessToken;
                            console.log("Access token acquired:", accessToken);
                            Shiny.setInputValue("access_token", accessToken);
                        })
                        .catch(error => {
                            console.error("Token acquisition error:", error);
                        });
                })
                .catch(error => {
                    console.error("Login error:", error);
                });
        }

        function getTokenPopup(request) {
            return msalInstance.acquireTokenSilent(request)
                .catch(() => msalInstance.acquireTokenPopup(request));
        }
    """)
)

def server(input, output, session):
    @output
    @render.text
    @reactive.event(input.access_token)
    def access_token_output():
        token = input.access_token()
        if token:
            return f"Access Token: {token}"
        else:
            return "No access token received yet."

app = App(app_ui, server)
