var darkmodeAutoSwitch = "time";

function setDarkmode(enable) {
    if (enable == true) {
        $("html").addClass("darkmode");
    } else {
        $("html").removeClass("darkmode");
    }
    $(window).trigger("scroll");
}

function toggleDarkmode() {
    if ($("html").hasClass("darkmode")) {
        setDarkmode(false);
        sessionStorage.setItem("Argon_Enable_Dark_Mode", "false");
    } else {
        setDarkmode(true);
        sessionStorage.setItem("Argon_Enable_Dark_Mode", "true");
    }
}

if (sessionStorage.getItem("Argon_Enable_Dark_Mode") == "true") {
    setDarkmode(true);
}

function toggleDarkmodeByPrefersColorScheme(media) {
    if (sessionStorage.getItem('Argon_Enable_Dark_Mode') == "false" || sessionStorage.getItem('Argon_Enable_Dark_Mode') == "true") {
        return;
    }
    if (media.matches) {
        setDarkmode(true);
    } else {
        setDarkmode(false);
    }
}

function toggleDarkmodeByTime() {
    if (sessionStorage.getItem('Argon_Enable_Dark_Mode') == "false" || sessionStorage.getItem('Argon_Enable_Dark_Mode') == "true") {
        return;
    }
    let hour = new Date().getHours();
    if (hour < 7 || hour >= 22) {
        setDarkmode(true);
    } else {
        setDarkmode(false);
    }
}

if (darkmodeAutoSwitch == 'system') {
    var darkmodeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    darkmodeMediaQuery.addListener(toggleDarkmodeByPrefersColorScheme);
    toggleDarkmodeByPrefersColorScheme(darkmodeMediaQuery);
}
if (darkmodeAutoSwitch == 'time') {
    toggleDarkmodeByTime();
}
if (darkmodeAutoSwitch == 'alwayson') {
    setDarkmode(true);
}

function toggleAmoledDarkMode() {
    $("html").toggleClass("amoled-dark");
    if ($("html").hasClass("amoled-dark")) {
        localStorage.setItem("Argon_Enable_Amoled_Dark_Mode", "true");
    } else {
        localStorage.setItem("Argon_Enable_Amoled_Dark_Mode", "false");
    }
}

if (localStorage.getItem("Argon_Enable_Amoled_Dark_Mode") == "true") {
    $("html").addClass("amoled-dark");
} else if (localStorage.getItem("Argon_Enable_Amoled_Dark_Mode") == "false") {
    $("html").removeClass("amoled-dark");
}
