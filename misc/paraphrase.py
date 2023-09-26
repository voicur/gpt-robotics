import requests

url = 'https://paraai.pro/'
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundarylMAZMorRpNuAotAw',
    'Cookie': 'ARRAffinity=5df9c96707bc13743796f4fc7fc6789fead10d5fb05a5244d8125dea6a19447b; ARRAffinitySameSite=5df9c96707bc13743796f4fc7fc6789fead10d5fb05a5244d8125dea6a19447b; session=eyJzZXNzaW9uX2lkIjoiYzA5MzU4OTYtNmMyYy00YzdiLWI3ZWItMDAyYzBjZDA1YzZhIn0.ZPfV6g.z03wNd41Pr_IKXXV3amExIigPfA',
    'DNT': '1',
    'Host': 'paraai.pro',
    'Origin': 'https://paraai.pro',
    'Referer': 'https://paraai.pro/index',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}
text_to_paraphrase = """

Title: The Rise of AI-Enabled Drones: Revolutionizing Industries and Empowering Humanity

Introduction:
Drones, also known as unmanned aerial vehicles (UAVs), have rapidly evolved over the past decade, transforming various industries and revolutionizing the way tasks are performed. The integration of artificial intelligence (AI) into drones has further propelled their capabilities, enabling them to execute complex tasks autonomously. This essay explores the profound impact of AI-enabled drones, highlighting their contributions to industries such as agriculture, delivery services, surveillance, and disaster management, while also discussing the ethical considerations surrounding their use.

Body:

1. Agriculture:
AI-enabled drones have emerged as a game-changer in agriculture, offering farmers valuable insights into crop health, irrigation management, and pest control. Equipped with advanced sensors and AI algorithms, these drones can gather real-time data on soil moisture, plant health, and growth patterns. By analyzing this information, farmers can make data-driven decisions, optimize resource allocation, and enhance crop yields while reducing the need for excessive pesticide usage. Furthermore, AI-powered drones can autonomously spray fertilizers or pesticides, precisely targeting affected areas, thus minimizing environmental impact.

2. Delivery Services:
The integration of AI and drones has the potential to revolutionize the delivery industry. Companies like Amazon are actively exploring the use of drones for last-mile delivery, enabling faster and more efficient delivery of packages. AI algorithms enable drones to navigate complex environments, avoid obstacles, and optimize their flight paths, ensuring safe and efficient delivery. With the ability to autonomously adapt to changing conditions, AI-enabled drones can significantly reduce delivery times, costs, and carbon emissions.

3. Surveillance and Security:
AI-enabled drones equipped with advanced cameras and sensors have proven invaluable in enhancing surveillance and security measures. These drones can autonomously patrol designated areas, detect suspicious activities, and identify potential threats. AI algorithms enable real-time analysis of video feeds, allowing for immediate response to security breaches or emergencies. Moreover, the integration of facial recognition technology with drones can aid in locating missing persons or identifying individuals of interest, enhancing public safety.

4. Disaster Management:
During natural disasters or emergencies, AI-enabled drones play a crucial role in gathering critical information, assessing damages, and aiding in search and rescue operations. Equipped with thermal cameras and AI algorithms, drones can quickly identify survivors in disaster-stricken areas, improving response times and potentially saving lives. Additionally, AI-powered drones can create detailed maps of affected areas, helping authorities allocate resources effectively and plan recovery efforts efficiently.

Ethical Considerations:
As with any technological advancement, the use of AI-enabled drones raises ethical concerns that must be addressed. Privacy concerns arise with the extensive surveillance capabilities of drones, requiring strict regulations to protect individuals' rights. Moreover, the potential for weaponization of AI-enabled drones necessitates clear guidelines and international agreements to prevent misuse and ensure responsible use.

Conclusion:
AI-enabled drones have emerged as a transformative force, revolutionizing various industries and empowering humanity with their capabilities. From optimizing agricultural practices to enhancing delivery services, surveillance, and disaster management, these drones offer immense potential for efficiency, safety, and economic growth. However, ethical considerations must be carefully addressed to ensure the responsible and beneficial deployment of AI-enabled drones, fostering a future where humans and technology coexist harmoniously for the betterment of society.


"""

data = f'''------WebKitFormBoundarylMAZMorRpNuAotAw
Content-Disposition: form-data; name="btnradio"

Model 1
------WebKitFormBoundarylMAZMorRpNuAotAw
Content-Disposition: form-data; name="input_text"

{text_to_paraphrase}------WebKitFormBoundarylMAZMorRpNuAotAw--'''

response = requests.post(url, headers=headers, data=data)

print(response.status_code)
print(response.text)