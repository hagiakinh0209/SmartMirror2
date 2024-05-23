let weather = {
    apiKey: "062d92a2646152d39eb7845a608226cb",   // Nhập key lấy từ openweathermap.org
    fetchWeather: function (city) {
        fetch(
            "https://api.openweathermap.org/data/2.5/weather?q=" +
            city +
            "&lang=en&units=metric&appid=" +
            this.apiKey
        )
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Không có địa điểm");
                }
                return response.json();
            })
            .then((data) => this.displayWeather(data));
    },
    displayWeather: function (data) {
        const { name } = data;
        const { icon, description } = data.weather[0];
        const { temp, humidity } = data.main;
        const { speed } = data.wind;
        const { country } = data.sys;
        document.querySelector(".city").innerText = name + " , " + country;
        document.querySelector(".may").src = "https://openweathermap.org/img/wn/" + icon + ".png";
        document.querySelector(".description").innerText = description;
        document.querySelector(".temp").innerText = temp + "°C";
        document.querySelector(".humidity").innerText =
            "Humidity: " + humidity + "%";
        document.querySelector(".wind").innerText =
            "Wind speed: " + speed + " km/h";
    },
    search: function () {
        this.fetchWeather(document.querySelector(".search-bar").value);
    },
};

// document.querySelector(".searchtiet button").addEventListener("click", function () {
//     weather.search();
// });

// document
//     .querySelector(".search-bar")
//     .addEventListener("keyup", function (event) {
//         if (event.key == "Enter") {
//             weather.search();
//         }
//     });
weather.fetchWeather("ho chi minh");
weather.search();