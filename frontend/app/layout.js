import "./globals.css";

export const metadata = {
  title: "HackTheFuture",
  description: "A futuristic app",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
