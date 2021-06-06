""""Module containing all css classes"""


class CssConst:
    """"Class containing all css classes"""

    # html_results const
    ADVANCED_ANALYSE_DATES = "#root > div > div > div > div.big-container > div > div > div.ant-card-head > div > div > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)"
    ADVANCED_ANALYSE_DURATION = "#root > div > div > div > div.big-container > div > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)"
    ADVANCED_ANALYSE_VOLATILITY = "#root > div > div > div > div.big-container > div > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)"
    ADVANCED_ANALYSE_TRADE = "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ADVANCED_ANALYSE_START_WALLET = "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    ADVANCED_ANALYSE_END_WALLET = "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ADVANCED_ANALYSE_GAIN = "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    ADVANCED_ANALYSE_RELATIVE_GAIN = "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    ADVANCED_ANALYSE_WINNING_PERIOD = "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ADVANCED_ANALYSE_LOSING_PERIOD = "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    ADVANCED_ANALYSE_AVERAGE_WIN = "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ADVANCED_ANALYSE_AVERAGE_LOSS = "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    ADVANCED_ANALYSE_WALLET_AVERAGE_INVESTMENT = (
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    )
    ADVANCED_ANALYSE_WALLET_MAXIMUM_INVESTMENT = (
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(6) > div:nth-child(2)"
    )
    ADVANCED_ANALYSE_WIN_LOSS_RATIO = "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ADVANCED_ANALYSE_RISK_REWARD_RATIO = "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    ADVANCED_ANALYSE_EXPECTED_RETURN = "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ADVANCED_ANALYSE_SHARPE_RATIO = "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    ADVANCED_ANALYSE_SORTINO_RATIO = "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    ADVANCED_ANALYSE_RISK_OF_DRAWDOWN = "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(6) > div:nth-child(2)"
    ADVANCED_ANALYSE_AVERAGE_DRAWDOWN = "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ADVANCED_ANALYSE_MAX_DRAWDOWN_INFORMATIONS = (
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    )

    # Backtest page
    BACKTEST_START_BTN = ".backtest-button"
    PAIRS_INPUT = "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(2) > select"
    DATES_INPUTS = "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div > app-form-datepicker > div > input"
    START_INPUT = "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline  div:nth-child(4) > app-form-datepicker > div > input"
    END_INPUT = "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(6) > app-form-datepicker > div > input"
    RECOMMEND_PAIRS = "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-published.ng-star-inserted > div.ng-star-inserted > div.backtest-container-published-left > app-strategy-published-meta > table > tbody > tr > td.col-2 > div > span > a"
    ANALYSE_TAB_DEEP_ANALYSE_LINK = "div.backtest-panel:nth-child(4) > div:nth-child(1) > a:nth-child(2)"
    ANALYSE_TAB_HOLD = ".analysis > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(5) > tr:nth-child(3) > td:nth-child(1) > app-value:nth-child(1) > span:nth-child(1)"
    EXCHANGE = ".control-exchanges"
    SERVER_PROBLEM = "#dialog-unique > app-dialog-alert-api > div > div.dialog-body > div > button"
    BINANCE_EXCHANGE = ".control-exchanges > option[value=binance]"
    GRAPH_TOP = (
        "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-graph > div > div.backtest-graph-top"
    )
    BALANCE_BUTTON = "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline div div.scope-balance-button"
    STARTING_AMOUNT_ONE = "#starting-amount-one"
    STARTING_AMOUNT_TWO = "#starting-amount-two"
    PROGRESS_PERCENT = "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-graph > div > div.backtest-graph-top.backtest-percent > div > div.col3"
    # strategy page
    STRAT_NAME = (
        "app-marketplace-details-page > div > div.layout-body > div > div > div.col-md-12.col-xl-8.main > div > div.card-header.card-header-strong > div > div:nth-child(2) > div.card-name > h2"
    )
    STRAT_NAME_BACKTEST = "div.backtest-container-header.toolbar > h2"
    STRAT_VERSION = ".backtest-container-published-left > app-strategy-published-meta:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > div:nth-child(1)"
    BACKTEST_BTN = "button.d-sm-inline-block"
    INSTALL_BTN = ".right > button:nth-child(1)"
    UPDATE_BTN = "body > app-root > div > app-marketplace-details-page > div > div.layout-body > div > div > div.col-md-12.col-xl-8.main > div > div.card-header.card-header-strong > div > div:nth-child(3) > button"
    # login page
    EMAIL_INPUT = "body > app-root > div > app-auth-login-page > div > div > div > form > div > div > div:nth-child(4) > input"
    PASSWORD_INPUT = "body > app-root > div > app-auth-login-page > div > div > div > form > div > div > div.form-group.form-required.mb-0 > input"
    TWO_FA_INPUT = "body > app-root > div > app-auth-login-page > div > div > div > form > div > div > div.form-group.mb-2 > input"
    LOG_IN_BTN = "body > app-root > div > app-auth-login-page > div > div > div > form > div > div > div:nth-child(8) > button"
    # root page
    USER_DROPDOWN = "body > app-root > div > app-dashboard-page > div > app-header > header > div.header-bottom > a.header-user"
    # other
    POPUP = "app-dialog-tutorial > div > div > div > button.btn.btn-primary"
    # last line logs selector
    LOGS_LAST_LINE = "app-logs > table > tbody > tr:last-child"
