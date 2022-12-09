import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders Удалить визуальный шум link", () => {
  render(<App />);
  const linkElement = screen.getByText("Удалить визуальный шум");
  expect(linkElement).toBeInTheDocument();
});

test("renders О системе link", () => {
  render(<App />);
  const linkElement = screen.getByText("О системе");
  expect(linkElement).toBeInTheDocument();
});

test("renders Выбрать файл link", () => {
  render(<App />);
  const linkElement = screen.getByText("Выбрать файл");
  expect(linkElement).toBeInTheDocument();
});
