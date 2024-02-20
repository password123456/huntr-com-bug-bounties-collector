# huntr.com bugs collector
New bug bounty(vulnerabilities) collector

![made-with-python][made-with-python]
![Python Versions][pyversion-button] [![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fpassword123456%2Fwatching_new_bounty_posting&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

[pyversion-button]: https://img.shields.io/pypi/pyversions/Markdown.svg
[made-with-python]: https://img.shields.io/badge/Made%20with-Python-1f425f.svg


# Requirements
- Chrome with GUI (If you encounter trouble with script execution, check the status of GPU features, if available.)
- ChromeDriver

![img](https://github.com/password123456/huntr-com-bug-bounties-collector/blob/main/huntr.com.png)

# Preview
```
# python3 main.py

*2024-02-20 16:14:47.836189*

1. Arbitrary File Reading due to Lack of Input Filepath Validation
- Feb 6th 2024 / High (CVE-2024-0964)
- gradio-app/gradio
- https://huntr.com/bounties/25e25501-5918-429c-8541-88832dfd3741/

2. View Barcode Image leads to Remote Code Execution
- Jan 31st 2024 / Critical (CVE: Not yet)
- dolibarr/dolibarr
- https://huntr.com/bounties/f0ffd01e-8054-4e43-96f7-a0d2e652ac7e/

```
(delimiter-based file database)
```
# vim feeds.db

1|2024-02-20 16:17:40.393240|7fe14fd58ca2582d66539b2fe178eeaed3524342|CVE-2024-0964|https://huntr.com/bounties/25e25501-5918-429c-8541-88832dfd3741/
2|2024-02-20 16:17:40.393987|c6b84ac808e7f229a4c8f9fbd073b4c0727e07e1|CVE: Not yet|https://huntr.com/bounties/f0ffd01e-8054-4e43-96f7-a0d2e652ac7e/
3|2024-02-20 16:17:40.394582|7fead9658843919219a3b30b8249700d968d0cc9|CVE: Not yet|https://huntr.com/bounties/d6cb06dc-5d10-4197-8f89-847c3203d953/
4|2024-02-20 16:17:40.395094|81fecdd74318ce7da9bc29e81198e62f3225bd44|CVE: Not yet|https://huntr.com/bounties/d875d1a2-7205-4b2b-93cf-439fa4c4f961/
5|2024-02-20 16:17:40.395613|111045c8f1a7926174243db403614d4a58dc72ed|CVE: Not yet|https://huntr.com/bounties/10e423cd-7051-43fd-b736-4e18650d0172/
```

## Notes
- This code is designed to parse HTML elements from huntr.com, so it may not function correctly if the HTML page structure changes. 
- In case of errors during parsing, exception handling has been included, so if it doesn't work as expected, please inspect the HTML source for any changes.
- If get in trouble In a typical cloud environment, scripts may not function properly within virtual machines (VMs).
