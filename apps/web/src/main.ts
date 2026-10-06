import { createApp } from "vue";

import "./design/base.css";
import App from "./App.vue";
import { createHardRouter } from "./app/router";

createApp(App).use(createHardRouter()).mount("#app");
