from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import config


class LinkedInJobsPage:
    # Seletor do elemento de entrada de pesquisa, você pode ter que atualizar isso se a página mudar
    SEARCH_INPUT = (By.CSS_SELECTOR, "input.jobs-search-box__text-input")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.JOBS_LINK = (By.CSS_SELECTOR, "a.global-nav__primary-link[data-test-app-aware-link][aria-current='page']")

    def open(self):
        # Navega até a página de login do LinkedIn
        self.driver.get("https://br.linkedin.com")

    def login(self):
        # Encontra o campo de e-mail e insere o e-mail
        email_field = self.driver.find_element(By.ID, "session_key")
        email_field.send_keys(config.email)

        # Encontra o campo de senha e insere a senha
        password_field = self.driver.find_element(By.ID, "session_password")
        password_field.send_keys(config.password)

        # Encontra o botão de entrar e clica
        login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

    def get_jobs_page(self):
        self.driver.get("https://www.linkedin.com/jobs/")

    def input_search_query(self, term):
        try:
            search_input = self.wait.until(EC.presence_of_element_located(self.SEARCH_INPUT))
            search_input.clear()
            search_input.send_keys(term)
            search_input.send_keys(Keys.ENTER)
            print('Search inserted')
        except TimeoutException:
            print("Não foi possível encontrar o elemento para fazer a pesquisa.")
        except Exception as e:
            print(f"Erro ao clicar no elemento para fazer a pesquisa de resultados: {e}")

    def get_jobs_quantity(self):
        try:
            # Espera pelo elemento que contém a quantidade de resultados e obtém o texto
            results_element = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.jobs-search-results-list__subtitle span")))
            results_text = results_element.text
            print("Quantidade de resultados:", results_text)
        except TimeoutException:
            print("Não foi possível encontrar o elemento com a quantidade de resultados.")
        except Exception as e:
            print(f"Erro ao obter a quantidade de resultados: {e}")

    def scrape_jobs(self):
        # Espera até que a lista de vagas seja carregada
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.scaffold-layout__list-container")))
        jobs_data = []
        
        # Identifica todos os elementos 'li' que representam os itens da vaga
        job_listings = self.driver.find_elements(By.CSS_SELECTOR, "ul.scaffold-layout__list-container > li")

        # Itera sobre cada item da vaga e extrai as informações
        for index in range(len(job_listings)):
            attempts = 0
            while attempts < 3:
                try:
                    # Re-localiza o item da vaga a cada iteração para evitar stale element
                    job = self.driver.find_elements(By.CSS_SELECTOR, "ul.scaffold-layout__list-container > li")[index]
                    # Extraia as informações aqui
                    job_title = job.find_element(By.CSS_SELECTOR, "strong").text
                    company_name = job.find_element(By.CSS_SELECTOR, "span.job-card-container__primary-description").text
                    job_location = job.find_element(By.CSS_SELECTOR, "li.job-card-container__metadata-item").text

                    # Adiciona as informações extraídas em uma lista de dicionários
                    jobs_data.append({
                        'title': job_title,
                        'company': company_name,
                        'location': job_location
                    })

                    # Se a informação foi extraída com sucesso, saia do loop
                    break
                except StaleElementReferenceException:
                    # Se o elemento se tornou stale, espera um pouco e tenta novamente
                    print(f"Tentativa {attempts + 1}: Stale element reference, re-try after short delay.")
                    time.sleep(1)
                    attempts += 1
                except Exception as e:
                    # Outros erros
                    print(f"Erro ao extrair dados de uma vaga: {e}")
                    break
        
        # Printa as informações no console
        for job in jobs_data:
            print(f"Vaga: {job['title']}")
            print(f"Empresa: {job['company']}")
            print(f"Localização: {job['location']}\n")

# Exemplo de como a classe acima seria utilizada
if __name__ == "__main__":
    # Inicialize o driver do navegador (neste caso, assumindo o Chrome)
    # Configurações do webdriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Crie um objeto da página
    linkedin_jobs_page = LinkedInJobsPage(driver)
    
    # Abra a página de empregos do LinkedIn
    linkedin_jobs_page.open()

    # Realiza login
    linkedin_jobs_page.login()
    time.sleep(15)

    # Clcik on jobs
    linkedin_jobs_page.get_jobs_page()

    # Digite a palavra desejada no campo de busca
    linkedin_jobs_page.input_search_query("fullstack javascript")

    # Lê a quantidade de resultados:
    linkedin_jobs_page.get_jobs_quantity()

    # Scrape jobs
    linkedin_jobs_page.scrape_jobs()

    # Aguarde alguns segundos para ver o resultado (opcional)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(LinkedInJobsPage.SEARCH_INPUT))

    driver.quit()
