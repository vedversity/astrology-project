import { DoshPage, doshMetadata } from "@/components/guides";

type Props = { params: Promise<{ dosha: string }> };

export async function generateMetadata({ params }: Props) {
  return doshMetadata("en", (await params).dosha);
}

export default async function Page({ params }: Props) {
  return <DoshPage lang="en" slug={(await params).dosha} />;
}
