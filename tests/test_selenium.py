# tests/test_selenium.py
import pytest
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# MODIFIEZ CETTE URL SI VOTRE SERVEUR REACT TOURNE SUR UN AUTRE PORT (ex: http://localhost:5173 ou http://localhost:3000)
FILE_PATH = "http://localhost:3000"

class TestTaskManager:

    def _login_user(self, driver):
        """Méthode utilitaire pour connecter automatiquement l'utilisateur par défaut."""
        driver.get(FILE_PATH)
        
        try:
            # Sélecteurs génériques par type (hautement compatibles React)
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            # Repère le bouton de soumission (par son type ou son texte de connexion)
            submit_button = driver.find_element(
                By.XPATH, "//button[@type='submit' or contains(text(), 'Connexion') or contains(text(), 'Login')]"
            )
            
            # Saisie des accès définis en base de données mémoire
            email_input.clear()
            email_input.send_keys("admin@test.com")
            password_input.clear()
            password_input.send_keys("password")
            submit_button.click()
            
            # Attend que l'interface bascule sur la liste de tâches après authentification
            WebDriverWait(driver, 10).until(
                lambda d: "tasks" in d.current_url.lower() or d.find_elements(By.TAG_NAME, "h1") or d.find_elements(By.CSS_SELECTOR, "input[placeholder*='tâche']")
            )
            
        except Exception as e:
            # Crée un snapshot visuel automatique en cas d'erreur de sélecteur au login
            driver.save_screenshot("debug_login_error.png")
            print(f"\n[DEBUG] Échec de la connexion. URL actuelle : {driver.current_url}")
            raise e

    def test_page_loads(self, driver):
        """Vérifie le chargement initial de l'application (Page d'authentification)."""
        driver.get(FILE_PATH)
        assert "Gestionnaire" in driver.title or "Task" in driver.title or driver.title != ""
        
        # S'assure que le formulaire attendu est bien rendu à l'écran
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )
        inputs = driver.find_elements(By.TAG_NAME, "input")
        assert len(inputs) >= 1

    def test_create_task(self, driver):
        """Scénario de création d'une nouvelle tâche."""
        self._login_user(driver)
        
        # Recherche du champ titre (souvent type text ou avec un placeholder adapté)
        title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[placeholder*='titre'], input[placeholder*='Tâche']"))
        )
        
        # Recherche facultative de la description (textarea ou second input)
        try:
            desc_input = driver.find_element(By.TAG_NAME, "textarea")
        except:
            desc_input = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")[1] # fallback sur le 2eme input text
            
        # Remplissage des champs
        title_input.clear()
        title_input.send_keys("Nouvelle Tâche Selenium")
        desc_input.clear()
        desc_input.send_keys("Description générée automatiquement pour le test")
        
        # Gestion optionnelle du menu déroulant de priorité (si existant)
        try:
            priority_select = Select(driver.find_element(By.TAG_NAME, "select"))
            priority_select.select_by_value("medium")
        except:
            pass # Ignore si votre interface n'expose pas de sélecteur brut
            
        # Clic sur le bouton d'enregistrement / ajout
        add_button = driver.find_element(
            By.XPATH, "//button[contains(@type, 'submit') or contains(text(), 'Ajouter') or contains(text(), 'Créer')]"
        )
        add_button.click()
        
        # Contrôle de la création : le titre doit apparaître à l'écran
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Nouvelle Tâche Selenium')]"))
        )

    def test_modify_task(self, driver):
        """Scénario de modification de la tâche exemple."""
        self._login_user(driver)
        
        # Repère l'élément textuel de la tâche exemple injectée d'office par le backend Node
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Tâche exemple')]"))
        )
        
        # Recherche le bouton d'édition associé (souvent un bouton "Modifier" ou une icône à proximité)
        edit_button = driver.find_element(
            By.XPATH, "//*[contains(text(), 'Tâche exemple')]/ancestor::*[local-name()='div' or local-name()='li']//button[contains(text(), 'Modifier') or contains(text(), 'Editer')]"
        )
        edit_button.click()
        
        # Met à jour le titre dans le champ qui s'est ouvert
        title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
        )
        title_input.clear()
        title_input.send_keys("Tâche exemple Modifiée")
        
        # Enregistre les modifications
        save_button = driver.find_element(
            By.XPATH, "//button[contains(text(), 'Enregistrer') or contains(text(), 'Sauvegarder') or contains(text(), 'Valider')]"
        )
        save_button.click()
        
        # Valide que le nouveau titre est appliqué graphiquement
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Tâche exemple Modifiée')]"))
        )

    def test_delete_task(self, driver):
        """Scénario de suppression d'une tâche."""
        self._login_user(driver)
        
        # Cible la tâche modifiée au test précédent ou la tâche exemple principale
        target_task_text = "Tâche exemple Modifiée" if "Tâche exemple Modifiée" in driver.page_source else "Tâche exemple"
        
        task_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{target_task_text}')]"))
        )
        
        # Trouve le bouton de suppression à l'intérieur du même conteneur parent
        delete_button = driver.find_element(
            By.XPATH, f"//*[contains(text(), '{target_task_text}')]/ancestor::*[local-name()='div' or local-name()='li']//button[contains(text(), 'Supprimer') or contains(text(), 'Delete')]"
        )
        delete_button.click()
        
        # Gère la présence éventuelle d'une boîte de dialogue de confirmation native (window.confirm)
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
        except:
            pass # Pas de pop-up native configurée, comportement classique
            
        # Confirme la disparition visuelle complète de la ligne de tâche
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.XPATH, f"//*[contains(text(), '{target_task_text}')]"))
        )
