import reflex as rx
import re
from . import expression_eval as ee
from . import utils as ut


class ExpressionInputState(rx.State):
    text = ""
    focused = False
    lastWord = "."

    async def onChange(self, text):
        self.text = text.lower()
        yield
        words = re.findall(r'[0-9a-zA-Z]+$', self.text)
        self.lastWord = "."
        if words:
            self.lastWord = words[-1]
        tokenSuggestionState = await self.get_state(TokenSuggestionState)
        tokenSuggestionState.tokens = ee.ExpressionEvaluator.getFilteredTokens(self.lastWord)
        if (tokenSuggestionState.tokens):
            tokenSuggestionState.hidden = False
        else:
            tokenSuggestionState.hidden = True
        result: ut.Result[float] = ee.ExpressionEvaluator().eval(self.text)
        decimalButtonState = await self.get_state(DecimalButtonState)
        hexButtonState = await self.get_state(HexButtonState)
        binaryButtonState = await self.get_state(BinaryButtonState)
        if (isinstance(result, ut.Success)):
            decimalButtonState.text = str(result.value)
            decimalButtonState.hidden = False
            if result.value.is_integer():
                resultInt = int(result.value)
                decimalButtonState.text = str(resultInt)
                hexButtonState.text = str(hex(resultInt & 0xFFFFFFFFFFFFFFFF))
                hexButtonState.hidden = False
                binaryButtonState.text = str(bin(resultInt & 0xFFFFFFFFFFFFFFFF))
                binaryButtonState.hidden = False
            else:
                hexButtonState.text = ""
                hexButtonState.hidden = True
                binaryButtonState.text = ""
                binaryButtonState.hidden = True
        elif (isinstance(result, ut.Failure)):
            decimalButtonState.text = ""
            decimalButtonState.hidden = True
            hexButtonState.text = ""
            hexButtonState.hidden = True
            binaryButtonState.text = ""
            binaryButtonState.hidden = True

    def onBlur(self, text):
        self.focused = False

    def onFocus(self, text):
        self.focused = True


class DecimalButtonState(rx.State):
    text = ""
    hidden = True

    def onClick(self):
        return rx.set_clipboard(self.text)


class HexButtonState(rx.State):
    text = ""
    hidden = True

    def onClick(self):
        return rx.set_clipboard(self.text)


class BinaryButtonState(rx.State):
    text = ""
    hidden = True

    def onClick(self):
        return rx.set_clipboard(self.text)


class GlobalKeyState(rx.State):
    async def onEsc(self, key):
        expressionInputState = await self.get_state(ExpressionInputState)
        tokenSuggestionState = await self.get_state(TokenSuggestionState)
        decimalButtonState = await self.get_state(DecimalButtonState)
        hexButtonState = await self.get_state(HexButtonState)
        binaryButtonState = await self.get_state(BinaryButtonState)
        expressionInputState.text = ""
        decimalButtonState.text = ""
        decimalButtonState.hidden = True
        hexButtonState.text = ""
        hexButtonState.hidden = True
        binaryButtonState.text = ""
        binaryButtonState.hidden = True
        tokenSuggestionState.hidden = True
        return rx.set_focus("expression-input")


class GlobalKeyWatcher(rx.Fragment):
    keys: rx.Var[list[str]] = []  # type: ignore
    on_key_down: rx.EventHandler[lambda ev: [ev.key]]

    def _get_imports(self) -> rx.utils.imports.ImportDict:  # type: ignore
        return rx.utils.imports.merge_imports(  # type: ignore
            super()._get_imports(),
            {
                "react": {
                    rx.utils.imports.ImportVar(  # type: ignore
                        tag="useEffect"
                    )
                }
            },
        )

    def _get_hooks(self) -> str | None:
        return """
            useEffect(() => {
                const handle_key = (_ev) => {
                    if (%s.includes(_ev.key))
                        %s
                }
                document.addEventListener("keydown", handle_key, false);
                return () => {
                    document.removeEventListener("keydown", handle_key, false);
                }
            })
            """ % (
            self.keys,
            str(
                rx.Var.create(
                    self.event_triggers["on_key_down"]
                )
            )
            + "(_ev)",
        )

    def render(self):
        return ""  # No visual element, hooks only


def index() -> rx.Component:
    return rx.fragment(
        navbar_icons(),
        GlobalKeyWatcher.create(
            keys=["Escape"],
            on_key_down=GlobalKeyState.onEsc,
        ),
        rx.vstack(
            rx.box(),
            rx.input(
                value=ExpressionInputState.text,
                id="expression-input",
                placeholder="Expression...",
                size="3",
                width="100%",
                on_change=ExpressionInputState.onChange,
                on_blur=ExpressionInputState.onBlur,
                on_focus=ExpressionInputState.onFocus,
            ),
            tokenSuggestionCard(),
            rx.vstack(
                rx.button(
                    DecimalButtonState.text,
                    variant="ghost",
                    on_click=DecimalButtonState.onClick,
                    display=rx.cond(DecimalButtonState.hidden, "none", "")
                ),
                rx.button(
                    HexButtonState.text,
                    variant="ghost",
                    on_click=HexButtonState.onClick,
                    display=rx.cond(DecimalButtonState.hidden, "none", "")
                ),
                rx.button(
                    BinaryButtonState.text,
                    variant="ghost",
                    on_click=BinaryButtonState.onClick,
                    display=rx.cond(DecimalButtonState.hidden, "none", "")
                ),
                align="center",
                width="100%"
            ),
            spacing="5",
            min_height="85vh",
            padding_x="10%",
            padding_y="2%",
        )
    )


class TokenSuggestionState(rx.State):
    tokens: list[str] = []
    hidden = True

    async def onItemClick(self, item):
        expressionInputState = await self.get_state(ExpressionInputState)
        tokenSuggestionState = await self.get_state(TokenSuggestionState)
        token = str(item)
        expression = str(expressionInputState.text)
        last_index = expression.rfind(expressionInputState.lastWord)
        newExpression = expression[:last_index]
        expressionInputState.text = (f"{newExpression}{token}")
        tokenSuggestionState.hidden = True
        tokenSuggestionState.tokens = []
        return rx.set_focus("expression-input")


def tokenItem(item) -> rx.Component:
    return rx.list.item(  # type: ignore
        rx.button(
            item,
            variant="ghost",
            on_click=lambda: TokenSuggestionState.onItemClick(item),  # type: ignore
        ),
    )


def tokenSuggestionCard():
    return rx.card(
        rx.list(  # type: ignore
            rx.foreach(TokenSuggestionState.tokens, tokenItem)
        ),
        display=rx.cond(TokenSuggestionState.hidden, "none", ""),
    )


def navbar_icons_item(
    text: str, icon: str, url: str
) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, size="4", weight="medium")
        ),
        href=url,
    )


def navbar_icons() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.image(
                    src="/icon.png",
                    width="2.25em",
                    height="auto",
                    border_radius="25%",
                ),
                rx.heading(
                    "Hacker Calculator", size="7", weight="bold"
                ),
                navbar_icons_item("", "info", "https://github.com/alexmarincu/hacker-calculator-web-app"),
                align_items="center",
            ),
            rx.color_mode.button(),
            justify="between",
            align_items="center",
        ),
        bg=rx.color("accent", 3),
        padding="1em",
        # position="fixed",
        # top="0px",
        # z_index="5",
        # width="100%",
    )


style = {
    "font_family": "JetBrains Mono",
}
app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;200;300;400;500;600;700;800&display=swap",
    ],
    style=style
)
app.add_page(index)
