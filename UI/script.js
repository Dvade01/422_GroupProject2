function switchTabs(hide, show) {
    let hideDiv = document.getElementById(hide);
    let showDiv = document.getElementById(show);

    hideDiv.style.display = 'none';
    showDiv.style.display = 'block';

}

function showLightTabs() {
    switchTabs('home-button-dark', 'home-button-light');
    switchTabs('email-button-dark', 'email-button-light');
    switchTabs('packet-button-dark', 'packet-button-light');
    switchTabs('geolocation-button-dark', 'geolocation-button-light');
    switchTabs('virus-button-dark', 'virus-button-light');
    switchTabs('account-button-dark', 'account-button-light');
    switchTabs('settings-button-dark', 'settings-button-light');
}

function tabButton(hide, show) {
    showLightTabs();
    switchTabs(hide, show)
}