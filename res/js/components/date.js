import Pikaday from "pikaday";

const translation_de = {
    previousMonth : "Vorheriger Monat",
    nextMonth     : "Nächster Monat",
    months        : ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"],
    weekdays      : ["Sonntag","Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag"],
    weekdaysShort : ["So","Mo","Di","Mi","Do","Fr","Sa"]
};

export default (el) => new Pikaday({
    field: el,
    firstDay: 1,
    i18n: translation_de
});
