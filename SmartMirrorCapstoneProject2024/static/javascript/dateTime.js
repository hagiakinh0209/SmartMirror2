const timeElement = document.getElementById("clock");
const dateElement = document.getElementById("date");

function updateTime() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();

    date = now.date
    const dateStr = `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDate()}`;
    // Format the string with leading zeroes
    const clockStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;

    timeElement.innerText = clockStr + " ";
    dateElement.innerText = dateStr;
}

updateTime();
setTimeout(updateTime, 60000);