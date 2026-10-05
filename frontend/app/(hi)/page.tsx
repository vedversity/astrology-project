import { HomePage, pageMetadata } from "@/components/pages";

export const generateMetadata = () => pageMetadata("hi", "/", "home");

export default function Page() {
  return <HomePage lang="hi" />;
}
