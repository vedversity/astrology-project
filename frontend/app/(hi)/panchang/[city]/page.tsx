import { CityPanchangPage, cityMetadata } from "@/components/guides";

type Props = { params: Promise<{ city: string }> };

export async function generateMetadata({ params }: Props) {
  return cityMetadata("hi", (await params).city);
}

export default async function Page({ params }: Props) {
  return <CityPanchangPage lang="hi" slug={(await params).city} />;
}
