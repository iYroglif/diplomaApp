import { useCallback, useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import "./App.css";
import { Navigation } from "./components/Navigation/Navigation";
import { UploadFile } from "./components/UploadFile/UploadFile";
import { Preview } from "./components/Preview/Preview";
import { Download } from "./components/Download/Download";
import { Login } from "./components/Login/Login";
import { Register } from "./components/Register/Register";
import { Logout } from "./components/Logout/Logout";
import { History } from "./components/History/History";
import { About } from "./components/About/About";
import { Footer } from "./components/Footer/Footer";
import { NotFound } from "./components/NotFound/NotFound";
import { User } from "./UserInterface";
import { useFetchJSON } from "./useFetchJSON";
import { loginURL } from "./api/urls";

export const App = () => {
  const [user, setUser] = useState<User>();
  const [data, error] = useFetchJSON<User>(loginURL);

  const handleSetUser = useCallback((user?: User) => {
    setUser(user);
  }, []);

  useEffect(() => {
    setUser(error ? undefined : data);
  }, [data, error]);

  return (
    <>
      <Navigation user={user} />
      <div className="main">
        <Routes>
          <Route path="/" element={<UploadFile />} />
          <Route path="/preview/:fileId" element={<Preview />} />
          <Route path="/download/:fileId" element={<Download />} />
          <Route path="/login" element={<Login setUser={handleSetUser} />} />
          <Route path="/register" element={<Register setUser={handleSetUser} />} />
          <Route path="/logout" element={<Logout setUser={handleSetUser} />} />
          <Route path="/history" element={<History />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      <Footer />
    </>
  );
};
