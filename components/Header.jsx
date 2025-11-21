import React from "react";
import { Routes, Route, NavLink, Link } from "react-router-dom";
import HomePage from "./HomePage";
import About from "../utils/About";
import Contact from "../utils/Contact";
import Process from "../utils/process";

export default function Header() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="bg-white/70 backdrop-blur-md border-b border-gray-200 shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

          {/* Title (click → Home) */}
          <Link
            to="/"
            className="text-2xl md:text-3xl font-extrabold bg-gradient-to-r
                       from-indigo-600 via-blue-500 to-cyan-400 bg-clip-text 
                       text-transparent tracking-wide cursor-pointer"
          >
            MetaData Extractor
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `relative font-medium transition duration-300 ${
                  isActive
                    ? "text-indigo-600"
                    : "text-gray-700 hover:text-indigo-500"
                }`
              }
            >
              Home
            </NavLink>

            <NavLink
              to="/About"
              className={({ isActive }) =>
                `relative font-medium transition duration-300 ${
                  isActive
                    ? "text-indigo-600"
                    : "text-gray-700 hover:text-indigo-500"
                }`
              }
            >
              About Project
            </NavLink>

            <NavLink
              to="/Contact"
              className={({ isActive }) =>
                `relative font-medium transition duration-300 ${
                  isActive
                    ? "text-indigo-600"
                    : "text-gray-700 hover:text-indigo-500"
                }`
              }
            >
              Contact
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="p-0">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/About" element={<About />} />
          <Route path="/Contact" element={<Contact />} />
          <Route path="/process" element={<Process />} />
        </Routes>
      </main>
    </div>
  );
}
