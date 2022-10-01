import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Link,
  Switch,
  Redirect,
} from "react-router-dom";
import { menus, routes } from "./routes/index";

import "antd/dist/antd.css";

function App() {
  return (
    <Router>
      <Switch>
                {routes.map((item) => {
                  return (
                    <Route
                      key={item.path}
                      exact
                      path={item.path}
                      component={item.component}
                    />
                  );
                })}
                <Redirect from="/" to="/home" />
              </Switch>
    </Router>
  );
}

export default App;
