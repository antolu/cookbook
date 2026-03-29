import React from 'react';
import { Link } from 'react-router-dom';
import { ChefHat, Search, Home, BookOpen, PenSquare } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <ChefHat className="h-8 w-8 text-primary-600" />
                <span className="text-xl font-bold text-gray-900">Cookbook</span>
              </Link>
            </div>

            <nav className="flex items-center space-x-4">
              <Link
                to="/"
                className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                <Home className="h-4 w-4" />
                <span>Home</span>
              </Link>
              <Link
                to="/recipes"
                className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                <BookOpen className="h-4 w-4" />
                <span>Recipes</span>
              </Link>
              <Link
                to="/search"
                className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                <Search className="h-4 w-4" />
                <span>Search</span>
              </Link>
              <Link
                to="/editor"
                className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50"
              >
                <PenSquare className="h-4 w-4" />
                <span>New Recipe</span>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-500 text-sm">
            <p>&copy; {new Date().getFullYear()} Cookbook</p>
          </div>
        </div>
      </footer>
    </div>
  );
};
